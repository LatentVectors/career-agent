"""CLI I/O commands for dumping and loading data to/from markdown files.

This module provides commands for exporting database objects to markdown files
for easy editing, and importing changes back to the database.
"""

from __future__ import annotations

import datetime
import re
from pathlib import Path
from typing import Any

import frontmatter
import typer
from rich.console import Console

from ..config import DATA_DIR
from .database import db_manager
from .models import CandidateResponse, Experience, JobPosting

console = Console()

# Create the main I/O CLI apps
dump_app = typer.Typer(help="Dump database objects to markdown files")
load_app = typer.Typer(help="Load database objects from markdown files")


# Import config for DATA_DIR
# Dump commands
@dump_app.command("experiences")
def dump_experiences(
    delete: bool = typer.Option(False, "--delete", help="Delete existing files before dumping"),
) -> None:
    """Dump all experiences to individual markdown files."""
    output_dir = DATA_DIR / "io" / "experience"
    _dump_experiences(output_dir, delete)


@dump_app.command("responses")
def dump_responses(
    delete: bool = typer.Option(False, "--delete", help="Delete existing file before dumping"),
) -> None:
    """Dump all candidate responses to a single markdown file."""
    output_file = DATA_DIR / "io" / "responses" / "data.md"
    _dump_responses(output_file, delete)


@dump_app.command("job-postings")
def dump_job_postings(
    delete: bool = typer.Option(False, "--delete", help="Delete existing files before dumping"),
) -> None:
    """Dump all job postings to individual markdown files."""
    output_dir = DATA_DIR / "io" / "job-posting"
    _dump_job_postings(output_dir, delete)


# Load commands
@load_app.command("experiences")
def load_experiences(
    delete: bool = typer.Option(False, "--delete", help="Delete experiences not found in files"),
) -> None:
    """Load experiences from individual markdown files."""
    input_dir = DATA_DIR / "io" / "experience"
    _load_experiences(input_dir, delete)


@load_app.command("responses")
def load_responses(
    delete: bool = typer.Option(False, "--delete", help="Delete responses not found in file"),
) -> None:
    """Load candidate responses from a single markdown file."""
    input_file = DATA_DIR / "io" / "responses" / "data.md"
    _load_responses(input_file, delete)


@load_app.command("job-postings")
def load_job_postings(
    delete: bool = typer.Option(False, "--delete", help="Delete job postings not found in files"),
) -> None:
    """Load job postings from individual markdown files."""
    input_dir = DATA_DIR / "io" / "job-posting"
    _load_job_postings(input_dir, delete)


def _parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Parse frontmatter from markdown content.

    Args:
        content: The markdown content with frontmatter

    Returns:
        Tuple of (frontmatter dict, content without frontmatter)

    Raises:
        ValueError: If frontmatter is malformed
    """
    try:
        post = frontmatter.loads(content)
        return dict(post.metadata), post.content
    except Exception as e:
        raise ValueError(f"Failed to parse frontmatter: {e}")


def _write_frontmatter(metadata: dict[str, Any]) -> str:
    """Write frontmatter to string format.

    Args:
        metadata: Dictionary of frontmatter data

    Returns:
        Frontmatter as string
    """
    post = frontmatter.Post("", **metadata)
    return frontmatter.dumps(post)


def _parse_response_section(content: str) -> dict[str, Any]:
    """Parse a single response section from the responses markdown file.

    Args:
        content: The content of a single response section

    Returns:
        Dictionary with response data

    Raises:
        ValueError: If section is malformed
    """
    lines = content.strip().split("\n")
    if not lines or not lines[0].startswith("#"):
        raise ValueError("Response section must start with '#'")

    # Parse header line
    header = lines[0]
    id_match = re.search(r"response_id:(\d+)", header)
    user_id_match = re.search(r"user_id:(\d+)", header)

    if not user_id_match:
        raise ValueError("Header must contain user_id")

    user_id = int(user_id_match.group(1))
    response_id = None
    if id_match:
        response_id = int(id_match.group(1))

    # Find prompt line
    prompt_line = None
    for i, line in enumerate(lines[1:], 1):
        if line.startswith("**Prompt:**"):
            prompt_line = i
            break

    if prompt_line is None:
        raise ValueError("Response section must contain '**Prompt:**' line")

    prompt = lines[prompt_line][10:].strip()  # Remove "**Prompt:**"

    # Get response content (everything after prompt until end)
    response_content = "\n".join(lines[prompt_line + 1 :]).strip()

    result = {"user_id": user_id, "prompt": prompt, "response": response_content}
    if response_id is not None:
        result["id"] = response_id

    return result


def _dump_experiences(output_dir: Path, delete: bool = False) -> None:
    """Dump all experiences to individual markdown files.

    Args:
        output_dir: Directory to write experience files
        delete: Whether to delete existing files first
    """
    if delete and output_dir.exists():
        for file in output_dir.glob("*.md"):
            file.unlink()

    output_dir.mkdir(parents=True, exist_ok=True)

    experiences = db_manager.experiences.get_all()

    for experience in experiences:
        # Create frontmatter
        frontmatter = {
            "id": experience.id,
            "user_id": experience.user_id,
            "title": experience.title,
            "company": experience.company,
            "location": experience.location,
            "start_date": experience.start_date.isoformat(),
            "end_date": experience.end_date.isoformat() if experience.end_date else None,
        }

        # Create markdown content
        content = _write_frontmatter(frontmatter) + "\n\n" + experience.content

        # Write to file
        filename = f"experience_{experience.id}.md"
        filepath = output_dir / filename
        filepath.write_text(content, encoding="utf-8")

    console.print(f"Dumped {len(experiences)} experiences to {output_dir}")


def _load_experiences(input_dir: Path, delete: bool = False) -> None:
    """Load experiences from markdown files.

    Args:
        input_dir: Directory containing experience files
        delete: Whether to delete experiences not found in files
    """
    if not input_dir.exists():
        raise ValueError(f"Input directory {input_dir} does not exist")

    # Get existing experience IDs for deletion check
    existing_ids = {exp.id for exp in db_manager.experiences.get_all()}
    found_ids = set()

    for filepath in input_dir.glob("*.md"):
        try:
            content = filepath.read_text(encoding="utf-8")
            frontmatter, body_content = _parse_frontmatter(content)

            # Validate required fields
            required_fields = ["user_id", "title", "company", "location", "start_date"]
            for field in required_fields:
                if field not in frontmatter or frontmatter[field] is None:
                    raise ValueError(f"Missing required field: {field}")

            # Parse dates
            start_date_str = str(frontmatter["start_date"])
            if isinstance(frontmatter["start_date"], datetime.date):
                start_date = frontmatter["start_date"]
            else:
                start_date = datetime.date.fromisoformat(start_date_str)

            end_date = None
            if frontmatter.get("end_date") and frontmatter["end_date"] not in (None, "null", ""):
                end_date_str = str(frontmatter["end_date"])
                if isinstance(frontmatter["end_date"], datetime.date):
                    end_date = frontmatter["end_date"]
                else:
                    end_date = datetime.date.fromisoformat(end_date_str)

            # Create or update experience
            experience_data = {
                "user_id": frontmatter["user_id"],
                "title": frontmatter["title"],
                "company": frontmatter["company"],
                "location": frontmatter["location"],
                "start_date": start_date,
                "end_date": end_date,
                "content": body_content.strip(),
            }

            if frontmatter.get("id"):
                # Update existing experience
                experience_id = frontmatter["id"]
                found_ids.add(experience_id)

                experience = db_manager.experiences.get_by_id(experience_id)
                if experience:
                    for key, value in experience_data.items():
                        setattr(experience, key, value)
                    db_manager.experiences.update(experience)
                    console.print(f"Updated experience {experience_id}")
                else:
                    console.print(f"Experience {experience_id} not found, skipping")
            else:
                # Create new experience
                new_experience = Experience(**experience_data)
                created_experience = db_manager.experiences.create(new_experience)
                console.print(f"Created new experience with ID {created_experience.id}")

        except Exception as e:
            console.print(f"Error processing {filepath}: {e}", style="red")

    # Handle deletions
    if delete:
        for exp_id in existing_ids - found_ids:
            if db_manager.experiences.delete(exp_id):
                console.print(f"Deleted experience {exp_id}")


def _dump_responses(output_file: Path, delete: bool = False) -> None:
    """Dump all candidate responses to a single markdown file.

    Args:
        output_file: File to write responses to
        delete: Whether to delete existing file first
    """
    if delete and output_file.exists():
        output_file.unlink()

    output_file.parent.mkdir(parents=True, exist_ok=True)

    responses = db_manager.candidate_responses.get_all()

    content_lines = []
    for response in responses:
        section = f"# response_id:{response.id} - user_id:{response.user_id}\n"
        section += f"**Prompt:** {response.prompt}\n\n"
        section += f"{response.response}\n\n"
        section += "---\n"
        content_lines.append(section)

    output_file.write_text("".join(content_lines), encoding="utf-8")
    console.print(f"Dumped {len(responses)} responses to {output_file}")


def _load_responses(input_file: Path, delete: bool = False) -> None:
    """Load candidate responses from markdown file.

    Args:
        input_file: File containing responses
        delete: Whether to delete responses not found in file
    """
    if not input_file.exists():
        raise ValueError(f"Input file {input_file} does not exist")

    content = input_file.read_text(encoding="utf-8")

    # Get existing response IDs for deletion check
    existing_ids = {resp.id for resp in db_manager.candidate_responses.get_all()}
    found_ids = set()

    # Split into sections
    sections = content.split("---\n")

    for section in sections:
        section = section.strip()
        if not section:
            continue

        try:
            response_data = _parse_response_section(section)

            # Validate required fields
            required_fields = ["user_id", "prompt", "response"]
            for field in required_fields:
                if field not in response_data or response_data[field] is None:
                    raise ValueError(f"Missing required field: {field}")

            if response_data.get("id"):
                # Update existing response
                response_id = response_data["id"]
                found_ids.add(response_id)

                response = db_manager.candidate_responses.get_by_id(response_id)
                if response:
                    response.user_id = response_data["user_id"]
                    response.prompt = response_data["prompt"]
                    response.response = response_data["response"]
                    db_manager.candidate_responses.update(response)
                    console.print(f"Updated response {response_id}")
                else:
                    console.print(f"Response {response_id} not found, skipping")
            else:
                # Create new response (no response_id provided)
                new_response = CandidateResponse(
                    user_id=response_data["user_id"],
                    prompt=response_data["prompt"],
                    response=response_data["response"],
                )
                created_response = db_manager.candidate_responses.create(new_response)
                console.print(f"Created new response with ID {created_response.id}")

        except Exception as e:
            console.print(f"Error processing response section: {e}", style="red")

    # Handle deletions
    if delete:
        for resp_id in existing_ids - found_ids:
            if db_manager.candidate_responses.delete(resp_id):
                console.print(f"Deleted response {resp_id}")


def _dump_job_postings(output_dir: Path, delete: bool = False) -> None:
    """Dump all job postings to individual markdown files.

    Args:
        output_dir: Directory to write job posting files
        delete: Whether to delete existing files first
    """
    if delete and output_dir.exists():
        for file in output_dir.glob("*.md"):
            file.unlink()

    output_dir.mkdir(parents=True, exist_ok=True)

    job_postings = db_manager.job_postings.get_all()

    for job_posting in job_postings:
        # Create frontmatter with id and company_id (title is in filename)
        frontmatter = {
            "id": job_posting.id,
            "company_id": job_posting.company_id,
        }

        # Create markdown content
        content = _write_frontmatter(frontmatter) + "\n\n" + job_posting.description

        # Write to file using title for filename
        safe_title = "".join(
            c for c in job_posting.title if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()
        safe_title = safe_title.replace(" ", "_")
        filename = f"{safe_title}.md"
        filepath = output_dir / filename
        filepath.write_text(content, encoding="utf-8")

    console.print(f"Dumped {len(job_postings)} job postings to {output_dir}")


def _load_job_postings(input_dir: Path, delete: bool = False) -> None:
    """Load job postings from markdown files.

    Args:
        input_dir: Directory containing job posting files
        delete: Whether to delete job postings not found in files
    """
    if not input_dir.exists():
        raise ValueError(f"Input directory {input_dir} does not exist")

    # Get existing job posting IDs for deletion check
    existing_ids = {jp.id for jp in db_manager.job_postings.get_all()}
    found_ids = set()

    for filepath in input_dir.glob("*.md"):
        try:
            content = filepath.read_text(encoding="utf-8")
            frontmatter, body_content = _parse_frontmatter(content)

            # Extract title from filename (remove .md extension and convert underscores to spaces)
            title = filepath.stem.replace("_", " ")

            # Check if this is a new job posting (no id or id is null)
            is_new_job = not frontmatter.get("id") or frontmatter["id"] is None

            if is_new_job:
                # Create new job posting
                # Create job posting data
                job_posting_data = {
                    "title": title,
                    "description": body_content.strip(),
                }

                # Add company_id if provided
                if frontmatter.get("company_id") and frontmatter["company_id"] is not None:
                    # Verify company exists
                    company = db_manager.companies.get_by_id(frontmatter["company_id"])
                    if company is None:
                        console.print(
                            f"Company {frontmatter['company_id']} not found, creating job posting without company",
                            style="yellow",
                        )
                    else:
                        job_posting_data["company_id"] = frontmatter["company_id"]

                # Create new job posting
                new_job_posting = JobPosting(**job_posting_data)
                created_job_posting = db_manager.job_postings.create(new_job_posting)
                console.print(
                    f"Created new job posting with ID {created_job_posting.id}: {created_job_posting.title}"
                )

            else:
                # Update existing job posting
                job_posting_id = frontmatter["id"]
                found_ids.add(job_posting_id)

                # Validate required fields for existing job postings
                required_fields = ["company_id"]
                for field in required_fields:
                    if field not in frontmatter or frontmatter[field] is None:
                        raise ValueError(
                            f"Missing required field for existing job posting: {field}"
                        )

                # Verify company exists
                company = db_manager.companies.get_by_id(frontmatter["company_id"])
                if company is None:
                    console.print(
                        f"Company {frontmatter['company_id']} not found, skipping {filepath}",
                        style="yellow",
                    )
                    continue

                job_posting = db_manager.job_postings.get_by_id(job_posting_id)
                if job_posting:
                    job_posting.company_id = frontmatter["company_id"]
                    job_posting.title = title
                    job_posting.description = body_content.strip()
                    db_manager.job_postings.update(job_posting)
                    console.print(f"Updated job posting {job_posting_id}: {job_posting.title}")
                else:
                    console.print(f"Job posting {job_posting_id} not found, skipping")

        except Exception as e:
            console.print(f"Error processing {filepath}: {e}", style="red")

    # Handle deletions
    if delete:
        for jp_id in existing_ids - found_ids:
            if db_manager.job_postings.delete(jp_id):
                console.print(f"Deleted job posting {jp_id}")
