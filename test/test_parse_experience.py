"""Unit tests for parse_experience module."""

import pytest
from src.resume.types import Experience
from src.storage.parse_experience import format_experience, parse_experience_file


class TestParseExperienceFile:
    """Test cases for parse_experience_file function."""

    def test_parse_experience_with_yaml_front_matter(self) -> None:
        """Test parsing an experience file with YAML front-matter."""
        content = """---
title: Senior Software Engineer
company: TechCorp Inc.
location: San Francisco, CA
start_date: 2020-01-15
end_date: 2023-06-30
points:
  - Led development of microservices architecture
  - Mentored junior developers
  - Improved system performance by 40%
---

This is the body content of the experience.

It can contain multiple paragraphs and markdown formatting.

- Additional bullet point
- Another accomplishment"""

        exp, body = parse_experience_file(content)

        assert isinstance(exp, Experience)
        assert exp.title == "Senior Software Engineer"
        assert exp.company == "TechCorp Inc."
        assert exp.location == "San Francisco, CA"
        assert exp.start_date == "2020-01-15"
        assert exp.end_date == "2023-06-30"
        assert exp.points == [
            "Led development of microservices architecture",
            "Mentored junior developers",
            "Improved system performance by 40%",
        ]

        # Body should contain everything after the YAML front-matter
        expected_body = """This is the body content of the experience.

It can contain multiple paragraphs and markdown formatting.

- Additional bullet point
- Another accomplishment"""
        assert body.strip() == expected_body.strip()

    def test_parse_experience_without_yaml_front_matter_raises_error(self) -> None:
        """Parsing a file without front-matter should raise a *ValueError*."""

        content = """This is a legacy experience file without YAML front-matter.

It contains some bullet points:
- First accomplishment
- Second accomplishment
- Third accomplishment

And some regular text."""

        with pytest.raises(ValueError, match="Missing YAML front-matter"):
            parse_experience_file(content)

    def test_parse_experience_with_empty_yaml(self) -> None:
        """Test parsing an experience file with empty YAML front-matter."""
        content = """---
---

This is the body content."""

        exp, body = parse_experience_file(content)

        assert isinstance(exp, Experience)
        assert exp.title == ""
        assert exp.company == ""
        assert exp.location == ""
        assert exp.start_date == ""
        assert exp.end_date == ""
        assert exp.points == []

        assert body.strip() == "This is the body content."

    def test_parse_experience_with_partial_yaml(self) -> None:
        """Test parsing an experience file with partial YAML data."""
        content = """---
title: Junior Developer
company: StartupXYZ
---

This is the body content."""

        exp, body = parse_experience_file(content)

        assert isinstance(exp, Experience)
        assert exp.title == "Junior Developer"
        assert exp.company == "StartupXYZ"
        assert exp.location == ""
        assert exp.start_date == ""
        assert exp.end_date == ""
        assert exp.points == []

        assert body.strip() == "This is the body content."

    def test_parse_experience_with_malformed_yaml(self) -> None:
        """Test parsing an experience file with malformed YAML raises ValueError."""
        content = """---
title: "Unclosed quote
company: TechCorp
---

This is the body content."""

        with pytest.raises(ValueError, match="Invalid YAML front-matter in experience file"):
            parse_experience_file(content)

    def test_parse_experience_with_invalid_experience_data(self) -> None:
        """Test parsing an experience file with invalid Experience data raises ValueError."""
        content = """---
title: 123  # title should be string, not int
company: TechCorp
location: San Francisco
start_date: 2020-01-15
end_date: 2023-06-30
---

This is the body content."""

        with pytest.raises(ValueError, match="Experience metadata failed validation"):
            parse_experience_file(content)

    def test_parse_experience_with_no_body(self) -> None:
        """Test parsing an experience file with only YAML front-matter."""
        content = """---
title: Senior Developer
company: TechCorp
location: Remote
start_date: 2020-01-15
end_date: Present
points:
  - Led team of 5 developers
  - Implemented CI/CD pipeline
---"""

        exp, body = parse_experience_file(content)

        assert isinstance(exp, Experience)
        assert exp.title == "Senior Developer"
        assert exp.company == "TechCorp"
        assert exp.location == "Remote"
        assert exp.start_date == "2020-01-15"
        assert exp.end_date == "Present"
        assert exp.points == [
            "Led team of 5 developers",
            "Implemented CI/CD pipeline",
        ]

        assert body.strip() == ""

    def test_parse_experience_with_complex_body(self) -> None:
        """Test parsing an experience file with complex body content."""
        content = """---
title: Full Stack Developer
company: WebCorp
location: New York, NY
start_date: 2019-03-01
end_date: 2022-12-31
points:
  - Built responsive web applications
  - Optimized database queries
---

# Project Highlights

## E-commerce Platform
- Developed a full-featured e-commerce platform using React and Node.js
- Implemented payment processing with Stripe
- Achieved 99.9% uptime

## Performance Improvements
- Reduced page load times by 60%
- Implemented lazy loading for images
- Added caching layer with Redis

## Team Collaboration
- Led code reviews for junior developers
- Conducted technical interviews
- Organized weekly knowledge sharing sessions"""

        exp, body = parse_experience_file(content)

        assert isinstance(exp, Experience)
        assert exp.title == "Full Stack Developer"
        assert exp.company == "WebCorp"
        assert exp.location == "New York, NY"
        assert exp.start_date == "2019-03-01"
        assert exp.end_date == "2022-12-31"
        assert exp.points == [
            "Built responsive web applications",
            "Optimized database queries",
        ]

        # Body should contain the markdown content
        assert "# Project Highlights" in body
        assert "## E-commerce Platform" in body
        assert "## Performance Improvements" in body
        assert "## Team Collaboration" in body


class TestFormatExperience:
    """Test cases for format_experience function."""

    def test_format_experience_with_all_fields(self) -> None:
        """Test formatting an experience with all fields populated."""
        exp = Experience(
            title="Senior Software Engineer",
            company="TechCorp Inc.",
            location="San Francisco, CA",
            start_date="2020-01-15",
            end_date="2023-06-30",
            points=[
                "Led development of microservices architecture",
                "Mentored junior developers",
                "Improved system performance by 40%",
            ],
        )
        body = """This is the body content of the experience.

It can contain multiple paragraphs and markdown formatting.

- Additional bullet point
- Another accomplishment"""

        result = format_experience(exp, body)

        # Should contain YAML front-matter
        assert "---" in result
        assert "title: Senior Software Engineer" in result
        assert "company: TechCorp Inc." in result
        assert "location: San Francisco, CA" in result
        assert "start_date: 2020-01-15" in result
        assert "end_date: 2023-06-30" in result
        assert "points:" in result
        assert "- Led development of microservices architecture" in result
        assert "- Mentored junior developers" in result
        assert "- Improved system performance by 40%" in result

        # Should contain body content
        assert "This is the body content of the experience." in result
        assert "It can contain multiple paragraphs and markdown formatting." in result
        assert "- Additional bullet point" in result
        assert "- Another accomplishment" in result

        # Should have proper structure
        lines = result.split("\n")
        assert lines[0] == "---"
        assert lines[-1] == ""
        assert "---" in lines[1:-1]  # Closing separator

    def test_format_experience_with_minimal_fields(self) -> None:
        """Test formatting an experience with minimal fields."""
        exp = Experience(
            title="Junior Developer",
            company="StartupXYZ",
            location="",
            start_date="",
            end_date="",
            points=[],
        )
        body = "Simple body content."

        result = format_experience(exp, body)

        assert "---" in result
        assert "title: Junior Developer" in result
        assert "company: StartupXYZ" in result
        assert "Simple body content." in result

        # Should not include empty fields in YAML
        assert "location:" not in result
        assert "start_date:" not in result
        assert "end_date:" not in result
        assert "points:" not in result

    def test_format_experience_roundtrip(self) -> None:
        """Test that format_experience and parse_experience_file work together."""
        original_exp = Experience(
            title="Full Stack Developer",
            company="WebCorp",
            location="Remote",
            start_date="2019-03-01",
            end_date="2022-12-31",
            points=[
                "Built responsive web applications",
                "Optimized database queries",
                "Led team of 3 developers",
            ],
        )
        original_body = """# Project Highlights

## E-commerce Platform
- Developed a full-featured e-commerce platform
- Implemented payment processing with Stripe

## Performance Improvements
- Reduced page load times by 60%
- Implemented lazy loading for images"""

        # Format the experience
        formatted = format_experience(original_exp, original_body)

        # Parse it back
        parsed_exp, parsed_body = parse_experience_file(formatted)

        # Should match the original
        assert parsed_exp.title == original_exp.title
        assert parsed_exp.company == original_exp.company
        assert parsed_exp.location == original_exp.location
        assert parsed_exp.start_date == original_exp.start_date
        assert parsed_exp.end_date == original_exp.end_date
        assert parsed_exp.points == original_exp.points
        assert parsed_body.strip() == original_body.strip()

    def test_format_experience_with_special_characters(self) -> None:
        """Test formatting an experience with special characters in content."""
        exp = Experience(
            title="DevOps Engineer",
            company="CloudCorp & Partners",
            location="Austin, TX",
            start_date="2021-01-01",
            end_date="Present",
            points=[
                "Managed AWS infrastructure (EC2, S3, RDS)",
                "Implemented CI/CD with Jenkins & GitLab",
                "Reduced deployment time by 70%",
            ],
        )
        body = """# Infrastructure Management

## AWS Services
- **EC2**: Managed 50+ instances across 3 regions
- **S3**: Implemented lifecycle policies for cost optimization
- **RDS**: Set up automated backups and monitoring

## CI/CD Pipeline
- Configured Jenkins for automated testing
- Integrated with GitLab for seamless deployments
- Achieved 99.9% deployment success rate"""

        result = format_experience(exp, body)

        # Should handle special characters properly
        assert "CloudCorp & Partners" in result
        assert "AWS infrastructure (EC2, S3, RDS)" in result
        assert "CI/CD with Jenkins & GitLab" in result
        assert "**EC2**: Managed 50+ instances" in result
        assert "**S3**: Implemented lifecycle policies" in result

        # Should parse back correctly
        parsed_exp, parsed_body = parse_experience_file(result)
        assert parsed_exp.company == "CloudCorp & Partners"
        assert "AWS infrastructure (EC2, S3, RDS)" in parsed_exp.points[0]
        assert "CI/CD with Jenkins & GitLab" in parsed_exp.points[1]
        assert "**EC2**: Managed 50+ instances" in parsed_body

    def test_format_experience_with_empty_body(self) -> None:
        """Test formatting an experience with empty body."""
        exp = Experience(
            title="Intern",
            company="TechStartup",
            location="Boston, MA",
            start_date="2023-06-01",
            end_date="2023-08-31",
            points=["Assisted with frontend development", "Learned React and TypeScript"],
        )
        body = ""

        result = format_experience(exp, body)

        assert "---" in result
        assert "title: Intern" in result
        assert "company: TechStartup" in result
        assert "location: Boston, MA" in result
        assert "start_date: 2023-06-01" in result
        assert "end_date: 2023-08-31" in result
        assert "points:" in result
        assert "- Assisted with frontend development" in result
        assert "- Learned React and TypeScript" in result

        # Should end with just the YAML front-matter
        lines = result.split("\n")
        assert lines[-2] == "---"
        assert lines[-1] == ""

        # Should parse back correctly
        parsed_exp, parsed_body = parse_experience_file(result)
        assert parsed_exp.title == "Intern"
        assert parsed_body.strip() == ""
