from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import jinja2
from loguru import logger
from PyPDF2 import PdfReader
from weasyprint import CSS, HTML  # type: ignore


def get_template_environment(templates_dir: str | Path) -> jinja2.Environment:
    """
    Create and configure Jinja2 template environment.

    Args:
        templates_dir: Path to the templates directory

    Returns:
        Configured Jinja2 environment
    """
    templates_path = Path(templates_dir)
    if not templates_path.exists():
        raise FileNotFoundError(f"Templates directory not found: {templates_path}")

    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(templates_path)),
        autoescape=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_template_to_html(
    template_name: str, context: Dict[str, Any], templates_dir: str | Path
) -> str:
    """
    Render a Jinja2 template to HTML string.

    Args:
        template_name: Name of the template file (e.g., 'resume_001.html')
        context: Data context for template rendering
        templates_dir: Path to the templates directory

    Returns:
        Rendered HTML string

    Raises:
        jinja2.TemplateNotFound: If template doesn't exist
        jinja2.TemplateError: If template rendering fails
    """
    try:
        env = get_template_environment(templates_dir)
        template = env.get_template(template_name)
        result: str = template.render(**context)
        return result
    except jinja2.TemplateNotFound:
        logger.error(f"Template not found: {template_name}", exception=True)
        raise
    except jinja2.TemplateError:
        logger.error(f"Template rendering failed: {template_name}", exception=True)
        raise


def convert_html_to_pdf(
    html_content: str, output_path: str | Path, css_string: Optional[str] = None
) -> Path:
    """
    Convert HTML content to PDF file.

    Args:
        html_content: HTML string to convert
        output_path: Path where PDF should be saved
        css_string: Optional CSS string for additional styling

    Returns:
        Path to the created PDF file

    Raises:
        Exception: If PDF generation fails
    """
    try:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Create HTML object
        html_doc = HTML(string=html_content)

        # Add CSS if provided
        css_docs = []
        if css_string:
            css_docs.append(CSS(string=css_string))

        # Generate PDF
        html_doc.write_pdf(str(output_path), stylesheets=css_docs)

        logger.debug(f"PDF generated successfully: {output_path}")
        return output_path

    except Exception:
        logger.error(f"Failed to generate PDF: {output_path}", exception=True)
        raise


def render_template_to_pdf(
    template_name: str,
    context: Dict[str, Any],
    output_path: str | Path,
    templates_dir: str | Path,
    css_string: Optional[str] = None,
) -> Path:
    """
    Render a Jinja2 template to PDF file.

    Args:
        template_name: Name of the template file (e.g., 'resume_001.html')
        context: Data context for template rendering
        output_path: Path where PDF should be saved
        templates_dir: Path to the templates directory
        css_string: Optional CSS string for additional styling

    Returns:
        Path to the created PDF file
    """
    # Render template to HTML
    html_content = render_template_to_html(template_name, context, templates_dir)

    # Convert HTML to PDF
    return convert_html_to_pdf(html_content, output_path, css_string)


def get_pdf_page_count(pdf_path: str | Path) -> int:
    """
    Get the number of pages in a PDF file.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Number of pages in the PDF

    Raises:
        FileNotFoundError: If PDF file doesn't exist
        Exception: If PDF reading fails
    """
    try:
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        with open(pdf_path, "rb") as file:
            reader = PdfReader(file)
            page_count = len(reader.pages)

        logger.debug(f"PDF page count: {page_count} pages in {pdf_path}")
        return page_count

    except Exception:
        logger.error(f"Failed to read PDF page count: {pdf_path}", exception=True)
        raise


def get_pdf_file_size(pdf_path: str | Path) -> int:
    """
    Get the file size of a PDF in bytes.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        File size in bytes

    Raises:
        FileNotFoundError: If PDF file doesn't exist
    """
    try:
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        file_size = pdf_path.stat().st_size
        logger.debug(f"PDF file size: {file_size} bytes for {pdf_path}")
        return file_size

    except Exception:
        logger.error(f"Failed to get PDF file size: {pdf_path}", exception=True)
        raise


def get_pdf_info(pdf_path: str | Path) -> Dict[str, Any]:
    """
    Get comprehensive information about a PDF file.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Dictionary containing page count, file size, and other metadata
    """
    try:
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # Get basic info
        page_count = get_pdf_page_count(pdf_path)
        file_size = get_pdf_file_size(pdf_path)

        # Get additional metadata
        with open(pdf_path, "rb") as file:
            reader = PdfReader(file)
            metadata = reader.metadata if reader.metadata else {}

        info = {
            "page_count": page_count,
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "metadata": metadata,
            "path": str(pdf_path),
        }

        logger.debug(f"PDF info retrieved: {info}")
        return info

    except Exception:
        logger.error(f"Failed to get PDF info: {pdf_path}", exception=True)
        raise


def list_available_templates(templates_dir: str | Path) -> list[str]:
    """
    List all available HTML templates in the templates directory.

    Args:
        templates_dir: Path to the templates directory

    Returns:
        List of template filenames
    """
    try:
        templates_path = Path(templates_dir)
        if not templates_path.exists():
            raise FileNotFoundError(f"Templates directory not found: {templates_path}")

        templates = [
            f.name for f in templates_path.iterdir() if f.is_file() and f.suffix.lower() == ".html"
        ]

        logger.debug(f"Found {len(templates)} templates in {templates_path}")
        return sorted(templates)

    except Exception:
        logger.error(f"Failed to list templates: {templates_dir}", exception=True)
        raise
