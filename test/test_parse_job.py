from pathlib import Path

import pytest
from src.storage.parse_job import Job, format_job, parse_job


class TestParseJob:
    """Test cases for parse_job function."""

    def test_parse_job_with_all_fields(self):
        """Test parsing a job with all fields populated."""
        content = """# Company Name
TechCorp Inc.

# Description
We are looking for a talented software engineer to join our team.

# Company Website
https://techcorp.com

# Company Email
careers@techcorp.com

# Company Overview
TechCorp is a leading technology company focused on innovation.

# My Interest
I'm excited about the opportunity to work on cutting-edge projects.

# Cover Letter
Dear Hiring Manager,

I am writing to express my interest in the software engineer position..."""

        result = parse_job(content)

        assert isinstance(result, Job)
        assert result.company_name == "TechCorp Inc."
        assert (
            result.description
            == "We are looking for a talented software engineer to join our team."
        )
        assert result.company_website == "https://techcorp.com"
        assert result.company_email == "careers@techcorp.com"
        assert (
            result.company_overview
            == "TechCorp is a leading technology company focused on innovation."
        )
        assert (
            result.my_interest
            == "I'm excited about the opportunity to work on cutting-edge projects."
        )
        assert (
            result.cover_letter
            == "Dear Hiring Manager,\n\nI am writing to express my interest in the software engineer position..."
        )

    def test_parse_job_with_required_fields_only(self):
        """Test parsing a job with only required fields (company_name and description)."""
        content = """# Company Name
StartupXYZ

# Description
Join our fast-growing startup as a developer."""

        result = parse_job(content)

        assert isinstance(result, Job)
        assert result.company_name == "StartupXYZ"
        assert result.description == "Join our fast-growing startup as a developer."
        assert result.company_website is None
        assert result.company_email is None
        assert result.company_overview is None
        assert result.my_interest is None
        assert result.cover_letter is None

    def test_parse_job_with_missing_company_name(self):
        """Test parsing a job with missing company name raises ValueError."""
        content = """# Description
We are looking for a developer.

# Company Website
https://example.com"""

        with pytest.raises(ValueError, match="Company name is required but not found in content"):
            parse_job(content)

    def test_parse_job_with_missing_description(self):
        """Test parsing a job with missing description raises ValueError."""
        content = """# Company Name
Example Corp

# Company Website
https://example.com"""

        with pytest.raises(ValueError, match="Description is required but not found in content"):
            parse_job(content)

    def test_parse_job_with_empty_company_name(self):
        """Test parsing a job with empty company name raises ValueError."""
        content = """# Company Name

# Description
We are looking for a developer."""

        with pytest.raises(ValueError, match="Company name is required but not found in content"):
            parse_job(content)

    def test_parse_job_with_empty_description(self):
        """Test parsing a job with empty description raises ValueError."""
        content = """# Company Name
Example Corp

# Description"""

        with pytest.raises(ValueError, match="Description is required but not found in content"):
            parse_job(content)

    def test_parse_job_with_multiline_content(self):
        """Test parsing a job with multiline content in fields."""
        content = """# Company Name
Multi-line Company
with extra content

# Description
This is a multi-line
description with
multiple lines of content

# Company Overview
This is a multi-line
company overview
with multiple lines"""

        result = parse_job(content)

        assert result.company_name == "Multi-line Company\nwith extra content"
        assert (
            result.description
            == "This is a multi-line\ndescription with\nmultiple lines of content"
        )
        assert (
            result.company_overview
            == "This is a multi-line\ncompany overview\nwith multiple lines"
        )

    def test_parse_job_with_whitespace_variations(self):
        """Test parsing a job with various whitespace patterns."""
        content = """# Company Name
   TechCorp Inc.   

# Description
   We are looking for a developer.   """

        result = parse_job(content)

        assert result.company_name == "TechCorp Inc."
        assert result.description == "We are looking for a developer."

    def test_parse_job_with_special_characters(self):
        """Test parsing a job with special characters in field content."""
        content = """# Company Name
TechCorp & Associates

# Description
We're looking for developers with 5+ years experience.

# Company Overview
We focus on AI/ML, cloud computing, and DevOps.

# My Interest
I'm excited about the opportunity to work with cutting-edge technologies!"""

        result = parse_job(content)

        assert result.company_name == "TechCorp & Associates"
        assert result.description == "We're looking for developers with 5+ years experience."
        assert result.company_overview == "We focus on AI/ML, cloud computing, and DevOps."
        assert (
            result.my_interest
            == "I'm excited about the opportunity to work with cutting-edge technologies!"
        )

    def test_parse_job_with_unknown_headers(self):
        """Test parsing a job with unknown headers (should be ignored)."""
        content = """# Company Name
TechCorp

# Description
We are hiring.

# Unknown Header
This should be ignored

# Another Unknown
This too should be ignored"""

        result = parse_job(content)

        assert result.company_name == "TechCorp"
        assert result.description == "We are hiring."
        # Unknown headers should not affect the result

    def test_parse_job_with_empty_sections(self):
        """Test parsing a job with empty sections."""
        content = """# Company Name
TechCorp

# Description
We are hiring.

# Company Website

# Company Email

# Company Overview"""

        result = parse_job(content)

        assert result.company_name == "TechCorp"
        assert result.description == "We are hiring."
        # Empty sections result in None values, not empty strings
        assert result.company_website is None
        assert result.company_email is None
        assert result.company_overview is None

    def test_parse_job_with_real_data_file(self):
        """Test parsing a job from an actual data file if it exists."""
        file_path = Path("data/job.md")
        if not file_path.exists():
            pytest.skip("Job data file not found")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        result = parse_job(content)

        # Should have required fields
        assert result.company_name is not None
        assert result.company_name != ""
        assert result.description is not None
        assert result.description != ""


class TestFormatJob:
    """Test cases for format_job function."""

    def test_format_job_with_all_fields(self):
        """Test formatting a job with all fields populated."""
        job = Job(
            company_name="TechCorp Inc.",
            description="We are looking for a talented software engineer.",
            company_website="https://techcorp.com",
            company_email="careers@techcorp.com",
            company_overview="TechCorp is a leading technology company.",
            my_interest="I'm excited about this opportunity.",
            cover_letter="Dear Hiring Manager,\n\nI am writing to express my interest...",
        )

        result = format_job(job)

        # Check that all fields are present in the formatted output
        assert "# Company Name" in result
        assert "TechCorp Inc." in result
        assert "# Description" in result
        assert "We are looking for a talented software engineer." in result
        assert "# Company Website" in result
        assert "https://techcorp.com" in result
        assert "# Company Email" in result
        assert "careers@techcorp.com" in result
        assert "# Company Overview" in result
        assert "TechCorp is a leading technology company." in result
        assert "# My Interest" in result
        assert "I'm excited about this opportunity." in result
        assert "# Cover Letter" in result
        assert "Dear Hiring Manager" in result

    def test_format_job_with_required_fields_only(self):
        """Test formatting a job with only required fields."""
        job = Job(company_name="StartupXYZ", description="Join our fast-growing startup.")

        result = format_job(job)

        # Check that required fields are present
        assert "# Company Name" in result
        assert "StartupXYZ" in result
        assert "# Description" in result
        assert "Join our fast-growing startup." in result

        # Check that optional fields are not present (since they're None)
        assert "https://" not in result
        assert "careers@" not in result

    def test_format_job_with_empty_optional_fields(self):
        """Test formatting a job with empty optional fields."""
        job = Job(
            company_name="TechCorp",
            description="We are hiring.",
            company_website="",
            company_email="",
            company_overview="",
            my_interest="",
            cover_letter="",
        )

        result = format_job(job)

        # Check that all field headers are present
        assert "# Company Name" in result
        assert "# Description" in result
        assert "# Company Website" in result
        assert "# Company Email" in result
        assert "# Company Overview" in result
        assert "# My Interest" in result
        assert "# Cover Letter" in result

        # Check that field values are present (even if empty)
        assert "TechCorp" in result
        assert "We are hiring." in result

    def test_format_job_roundtrip(self):
        """Test that format_job and parse_job work together correctly."""
        original_content = """# Company Name
TechCorp Inc.

# Description
We are looking for a talented software engineer.

# Company Website
https://techcorp.com

# Company Overview
TechCorp is a leading technology company."""

        # Parse the original content
        job = parse_job(original_content)

        # Format it back to string
        formatted_content = format_job(job)

        # Parse the formatted content again
        job_roundtrip = parse_job(formatted_content)

        # The jobs should be equivalent
        assert job.company_name == job_roundtrip.company_name
        assert job.description == job_roundtrip.description
        assert job.company_website == job_roundtrip.company_website
        assert job.company_overview == job_roundtrip.company_overview

    def test_format_job_field_ordering(self):
        """Test that format_job maintains consistent field ordering."""
        job = Job(
            company_name="TechCorp",
            description="We are hiring.",
            company_website="https://techcorp.com",
            company_email="careers@techcorp.com",
        )

        result = format_job(job)

        # Check that fields appear in the expected order
        lines = result.strip().split("\n")
        field_headers = [line for line in lines if line.startswith("# ")]

        expected_order = [
            "# Company Name",
            "# Description",
            "# Company Website",
            "# Company Email",
            "# Company Overview",
            "# My Interest",
            "# Cover Letter",
        ]

        assert field_headers == expected_order

    def test_format_job_with_special_characters(self):
        """Test formatting a job with special characters."""
        job = Job(
            company_name="TechCorp & Associates",
            description="We're looking for developers with 5+ years experience.",
            company_overview="We focus on AI/ML, cloud computing, and DevOps.",
            my_interest="I'm excited about the opportunity!",
        )

        result = format_job(job)

        # Check that special characters are preserved
        assert "TechCorp & Associates" in result
        assert "We're looking for developers with 5+ years experience." in result
        assert "We focus on AI/ML, cloud computing, and DevOps." in result
        assert "I'm excited about the opportunity!" in result
