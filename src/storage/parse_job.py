import re

from src.schemas import Job


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
        "Parsed Requirements": "parsed_requirements",
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

            # Special handling for parsed_requirements
            if field_name == "parsed_requirements":
                # Extract requirements from lines starting with "-"
                requirements = []
                for line in content_text.split("\n"):
                    line = line.strip()
                    if line.startswith("-"):
                        # Remove the "-" and any leading/trailing whitespace
                        requirement = line[1:].strip()
                        if requirement:  # Only add non-empty requirements
                            requirements.append(requirement)
                # Only set requirements if we found any, otherwise leave as None
                if requirements:
                    field_values[field_name] = requirements
            else:
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
        parsed_requirements=field_values.get("parsed_requirements"),
        my_interest=field_values.get("my_interest"),
        cover_letter=field_values.get("cover_letter"),
    )


def format_job(job: Job) -> str:
    """Format a job to a string."""
    content = ""

    # Define the order of fields for consistent formatting
    field_order = [
        ("company_name", "Company Name"),
        ("description", "Description"),
        ("company_website", "Company Website"),
        ("company_email", "Company Email"),
        ("company_overview", "Company Overview"),
        ("parsed_requirements", "Parsed Requirements"),
        ("my_interest", "My Interest"),
        ("cover_letter", "Cover Letter"),
    ]

    for field_name, field_display in field_order:
        value = getattr(job, field_name)

        content += f"# {field_display}\n"

        if field_name == "parsed_requirements":
            if value:
                # Format requirements as bullet points
                for requirement in value:
                    content += f"- {requirement}\n"
            # Always include the section header even if empty
        elif value:
            content += f"{value}\n"

        content += "\n"

    return content
