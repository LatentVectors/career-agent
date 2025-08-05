from __future__ import annotations

from pydantic import BaseModel, Field


class ResumeData(BaseModel):
    """Complete resume data structure."""

    name: str = Field(..., description="Full name")
    title: str = Field(..., description="Professional title")
    email: str = Field(..., description="Email address")
    phone: str = Field(..., description="Phone number")
    linkedin_url: str = Field(..., description="LinkedIn profile URL")
    professional_summary: str = Field(..., description="Professional summary/objective")
    experience: list[ResumeExperience] = Field(
        default_factory=list, description="List of work experiences"
    )
    education: list[ResumeEducation] = Field(
        default_factory=list, description="List of educational background"
    )
    skills: list[str] = Field(default_factory=list, description="List of skills and technologies")
    certifications: list[ResumeCertification] = Field(
        default_factory=list, description="List of certifications"
    )


class ResumeExperience(BaseModel):
    """Work experience information for a resume."""

    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location")
    start_date: str = Field(..., description="Start date of employment")
    end_date: str = Field(..., description="End date of employment (or 'Present')")
    points: list[str] = Field(default_factory=list, description="List of experience points")


class ResumeEducation(BaseModel):
    """Education information for a resume."""

    degree: str = Field(..., description="The degree obtained")
    major: str = Field(..., description="The field of study")
    institution: str = Field(..., description="The educational institution")
    grad_date: str = Field(..., description="Graduation date")


class ResumeCertification(BaseModel):
    """Certification information for a resume."""

    title: str = Field(..., description="The certification title")
    date: str = Field(..., description="The date the certification was obtained")
