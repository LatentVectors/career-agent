import re
import unicodedata
from pathlib import Path
from typing import AsyncIterator, Iterator, Optional, Set, Union

import requests
from bs4 import BeautifulSoup, Tag
from langchain.schema import Document
from langchain_core.document_loaders import BaseLoader
from pydantic import BaseModel

URL = "https://paulgraham.com/articles.html"


class Article(BaseModel):
    url: str
    title: str
    filename: str


def scrape_paul_graham(download_dir: Path) -> None:
    """Scrape the Paul Graham website and save the articles to the download directory."""
    current_articles: Set[str] = set()
    for file in download_dir.glob("*.html"):
        current_articles.add(file.name.split(".")[0])
    print(f"Found {len(current_articles)} articles in the download directory")

    articles = get_articles()
    print(f"Found {len(articles)} articles to download")
    for article in articles:
        if article.filename in current_articles:
            print(f"Skipping {article.title} because it already exists")
            continue
        try:
            response = requests.get(article.url)
            response.raise_for_status()
        except Exception as e:
            print(f"Error downloading {article.url}: {e}")
            continue

        with open(download_dir / f"{article.filename}.html", "w") as f:
            f.write(response.text)
        print(f"Downloaded {article.title}")


def get_articles() -> list[Article]:
    """Get all the article URLs from the Paul Graham website."""
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table")
    table = tables[2]
    if isinstance(table, Tag):
        urls = []
        for a in table.find_all("a", href=True):
            if isinstance(a, Tag):
                href = str(a["href"])
                if href and not href.startswith("https://"):
                    url = f"{URL}/{href}"
                    filename = title_to_filename(a.text)
                    urls.append(Article(url=url, title=a.text, filename=filename))
        return urls
    else:
        return []


def title_to_filename(title: str) -> str:
    """Convert a title to a safe filename across operating systems.

    Handles special characters, non-ASCII characters, and ensures the filename
    follows conventions that work across Windows, macOS, and Linux.
    """

    # Normalize unicode characters
    normalized = unicodedata.normalize("NFKD", title)
    # Remove accents by keeping only ASCII chars
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    # Replace spaces and other unsafe characters with hyphens
    # Add more unsafe characters including /, \, :, *, ?, ", <, >, |, etc.
    safe_filename = re.sub(r"[^\w.-]", "-", ascii_text)
    # Remove consecutive hyphens
    safe_filename = re.sub(r"--+", "-", safe_filename)
    # Remove leading/trailing hyphens and dots
    safe_filename = safe_filename.strip("-.")
    # Handle empty filenames
    if not safe_filename:
        return "unnamed-article"
    # Ensure we don't exceed reasonable filename length
    if len(safe_filename) > 100:
        safe_filename = safe_filename[:100]
    # Convert to lowercase for consistency
    return safe_filename.lower()


class PaulGrahamHTMLLoader(BaseLoader):
    """Load and clean a Paul Graham HTML file."""

    def __init__(self, file_path: str):
        """Initialize the loader with the file path.

        Args:
            file_path (str): Path to the HTML file.
        """
        self.file_path = file_path

    def lazy_load(self) -> Iterator[Document]:
        """Lazy load the document."""
        file_path = Path(self.file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        doc = parse_doc(html_content, file_path)
        yield doc

    async def alazy_load(self) -> AsyncIterator[Document]:
        """Lazy load the document asynchronously."""
        import aiofiles

        file_path = Path(self.file_path)
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            html_content = await f.read()
            doc = parse_doc(html_content, file_path)
            yield doc


def parse_doc(html_content: str, file_path: Path) -> Document:
    """Parse the document."""
    soup = BeautifulSoup(html_content, "html.parser")
    title: str = soup.title.string if soup.title else ""  # type: ignore

    # Select the main content area if possible (e.g., body). Adjust if needed.
    tables = soup.find_all("table")
    if not isinstance(tables, list) or len(tables) < 3:
        raise ValueError(f"Could not find <body> tag in {file_path}")

    content = soup.find("font", attrs={"size": "2", "face": "verdana"})
    if not content:
        raise ValueError(f"Could not find <font> tag in {file_path}")
    if not isinstance(content, Tag):
        raise ValueError(f"Could not find <font> tag in {file_path}")

    final_text_parts = []
    # Iterate through all descendant strings and tags within the content area
    for element in content.descendants:
        if isinstance(element, str):
            # This is a text node
            # Replace literal '\n' with space, strip leading/trailing whitespace
            cleaned_text = element.strip().replace("\n", " ")
            # Append if it's not just whitespace
            if cleaned_text:
                final_text_parts.append(cleaned_text)
        elif isinstance(element, Tag) and element.name == "br":
            # This is a <br> tag, treat it as a paragraph break ('\n')
            # Avoid adding multiple consecutive newlines if <br> tags are stacked
            # or if the previous element already resulted in a newline implicitly.
            # We'll handle collapsing multiple newlines later.
            final_text_parts.append("\n")

    # Join the parts. Use space as a default separator between text parts
    # that were not separated by <br>.
    raw_joined_text = " ".join(final_text_parts)
    cleaned_full_text = clean_text_whitespace(raw_joined_text)

    # Initialize metadata
    metadata: dict[str, Union[str, int]] = {
        "author": "Paul Graham",
        "filename": file_path.name,
        "title": title,
    }
    date = parse_date(cleaned_full_text)
    if date:
        metadata["date"] = date.date
        metadata["month"] = date.month
        metadata["year"] = date.year

    doc = Document(page_content=cleaned_full_text, metadata=metadata)
    return doc


def clean_text_whitespace(content: str) -> str:
    """Clean the text whitespace."""
    cleaned_full_text = re.sub(r"\s+\n+\s+", "\n", content)
    cleaned_full_text = re.sub(r"\n\s*\n", "\n", cleaned_full_text)
    cleaned_full_text = re.sub(r" +", " ", cleaned_full_text).strip()
    return cleaned_full_text


class ParsedDate(BaseModel):
    month: int
    year: int
    date: str


def parse_date(content: str) -> Optional[ParsedDate]:
    """Parse the date from the content."""
    months = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12,
    }
    date_pattern = r"(" + "|".join(months.keys()) + r")\s+(\d{4})"
    date_match = re.search(date_pattern, content)
    if date_match:
        month = date_match.group(1)
        year = date_match.group(2)
        return ParsedDate(month=months[month], year=int(year), date=date_match.group(0))
    return None
