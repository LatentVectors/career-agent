from __future__ import annotations

from pydantic import BaseModel, Field


# I need to get the users name, email, phone, linkedin_url, education, and certifications.
# professional_summary, experience, and skills should all come from generated content.
# I need to enhance past experience with predefined metadata.
class ResumeData(BaseModel):
    """Complete resume data structure."""

    name: str = Field(..., description="Full name")
    title: str = Field(..., description="Professional title")
    email: str = Field(..., description="Email address")
    phone: str = Field(..., description="Phone number")
    linkedin_url: str = Field(..., description="LinkedIn profile URL")
    professional_summary: str = Field(..., description="Professional summary/objective")
    experience: list[Experience] = Field(
        default_factory=list, description="List of work experiences"
    )
    education: list[Education] = Field(
        default_factory=list, description="List of educational background"
    )
    skills: list[str] = Field(default_factory=list, description="List of skills and technologies")
    certifications: list[Certification] = Field(
        default_factory=list, description="List of certifications"
    )


class Education(BaseModel):
    """Education information for a resume."""

    degree: str = Field(..., description="The degree obtained")
    major: str = Field(..., description="The field of study")
    institution: str = Field(..., description="The educational institution")
    grad_date: str = Field(..., description="Graduation date")


class Certification(BaseModel):
    """Certification information for a resume."""

    title: str = Field(..., description="The certification title")
    date: str = Field(..., description="The date the certification was obtained")


class Experience(BaseModel):
    """Work experience information for a resume."""

    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location")
    start_date: str = Field(..., description="Start date of employment")
    end_date: str = Field(..., description="End date of employment (or 'Present')")
    points: list[str] = Field(
        default_factory=list, description="List of accomplishments and responsibilities"
    )


class UserProfile(BaseModel):
    """Top-level personal information.

    Validation rules:
    • *email* – must be a valid e-mail address when non-empty.
    • *phone* – ``(###)-###-####`` when non-empty.
    • *linkedin_url* – valid URL which includes the domain *linkedin.com* when non-empty.
    """

    name: str = Field("", description="Full name")
    email: str = Field(
        "",
        description="Email address",
        pattern=r"^(?:[^@\s]+@[^@\s]+\.[^@\s]+)?$",
    )
    phone: str = Field(
        "",
        description="Phone number – (###)-###-####",
        pattern=r"^(?:\(\d{3}\)-\d{3}-\d{4})?$",
    )
    linkedin_url: str = Field(
        "",
        description="LinkedIn profile URL",
        pattern=r"^(?:https?://(?:www\.)?linkedin\.com/.*)?$",
    )

    education: list[Education] = Field(default_factory=list, description="Education entries")
    certifications: list[Certification] = Field(default_factory=list, description="Certifications")

    @property
    def is_empty(self) -> bool:  # noqa: D401
        """Return *True* when no meaningful data has been set."""

        scalar_set = any([self.name, self.email, self.phone, self.linkedin_url])
        return not scalar_set and not self.education and not self.certifications
