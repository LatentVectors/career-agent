import re
from typing import Optional

from pydantic import BaseModel


class Job(BaseModel):
    company_name: str
    description: str
    company_website: Optional[str] = None
    company_email: Optional[str] = None
    company_overview: Optional[str] = None
    my_interest: Optional[str] = None
    cover_letter: Optional[str] = None


def parse_job(content: str) -> Job:
    """Parse a job from the file storage.

    Args:
        content: String content containing job information with # headers

    Returns:
        Job object with parsed information

    Raises:
        ValueError: If required fields (company_name, description) are missing
    """
    # Define field mappings from header names to Job model fields
    field_mappings = {
        "Company Name": "company_name",
        "Description": "description",
        "Company Website": "company_website",
        "Company Email": "company_email",
        "Company Overview": "company_overview",
        "My Interest": "my_interest",
        "Cover Letter": "cover_letter",
    }

    # Parse content by splitting on # headers
    sections = re.split(r"\s*#\s+", content.strip())

    # Initialize field values
    field_values = {}

    for section in sections:
        if not section.strip():
            continue

        # Split on first newline to separate header from content
        lines = section.strip().split("\n", 1)
        if len(lines) < 2:
            continue

        header = lines[0].strip()
        content_text = lines[1].strip()

        # Map header to field name
        if header in field_mappings:
            field_name = field_mappings[header]
            field_values[field_name] = content_text

    # Validate required fields
    if "company_name" not in field_values or not field_values["company_name"]:
        raise ValueError("Company name is required but not found in content")

    if "description" not in field_values or not field_values["description"]:
        raise ValueError("Description is required but not found in content")

    # Create Job object with parsed values
    return Job(
        company_name=field_values.get("company_name", ""),
        description=field_values.get("description", ""),
        company_website=field_values.get("company_website"),
        company_email=field_values.get("company_email"),
        company_overview=field_values.get("company_overview"),
        my_interest=field_values.get("my_interest"),
        cover_letter=field_values.get("cover_letter"),
    )


def format_job(job: Job) -> str:
    """Format a job to a string."""
    content = ""
    for field, value in job.model_dump().items():
        field_name = field.replace("_", " ").title()
        content += f"# {field_name}\n"
        if value:
            content += f"{value}\n"
        content += "\n"
    return content
