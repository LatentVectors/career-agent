"""Database adapter functions for resume generation.

This module provides functions to fetch and transform user data from the database
to ResumeData format for resume generation.
"""

from __future__ import annotations

from datetime import date
from typing import Literal, TypedDict

from loguru import logger

from src.db.database import DatabaseManager, db_manager
from src.db.models import CandidateResponse, Certification, Education, Experience, User
from src.features.resume.types import (
    ResumeCertification,
    ResumeData,
    ResumeEducation,
    ResumeExperience,
)


class UserData(TypedDict):
    """Type definition for user data returned by fetch_user_data."""

    user: User
    education: list[Education]
    certifications: list[Certification]


MissingRequiredField = Literal["first_name", "last_name", "email"]
MissingOptionalField = Literal[
    "phone", "linkedin_url", "education", "experience", "candidate_responses"
]


def fetch_user_data(user_id: int, db_manager_instance: DatabaseManager | None = None) -> UserData:
    """Fetch user, education, and certification data from database.

    Args:
        user_id: The user's ID
        db_manager_instance: Optional database manager instance. Defaults to global db_manager.

    Returns:
        UserData containing user, education list, and certification list

    Raises:
        ValueError: If user is not found
    """
    # Use provided db_manager or fall back to global
    db = db_manager_instance or db_manager

    # Fetch user data
    user = db.users.get_by_id(user_id)
    if not user:
        raise ValueError(f"User with ID {user_id} not found")

    # Fetch education data
    education_list = db.educations.get_by_user_id(user_id)

    # Fetch certification data
    certification_list = db.certifications.get_by_user_id(user_id)

    return {
        "user": user,
        "education": education_list,
        "certifications": certification_list,
    }


def fetch_experience_data(
    user_id: int, db_manager_instance: DatabaseManager | None = None
) -> list[Experience]:
    """Fetch user experience data from database.

    Args:
        user_id: The user's ID
        db_manager_instance: Optional database manager instance. Defaults to global db_manager.

    Returns:
        List of user experiences
    """
    db = db_manager_instance or db_manager
    return db.experiences.get_by_user_id(user_id)


def fetch_candidate_responses(
    user_id: int, db_manager_instance: DatabaseManager | None = None
) -> list[CandidateResponse]:
    """Fetch candidate responses from database.

    Args:
        user_id: The user's ID
        db_manager_instance: Optional database manager instance. Defaults to global db_manager.

    Returns:
        List of candidate responses
    """
    db = db_manager_instance or db_manager
    return db.candidate_responses.get_by_user_id(user_id)


def _format_date(date_obj: date | None) -> str:
    """Format a date object to string representation.

    Args:
        date_obj: Date object to format

    Returns:
        Formatted date string (MMM YYYY format)
    """
    if not date_obj:
        return "Present"

    month_names = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    return f"{month_names[date_obj.month - 1]} {date_obj.year}"


def _format_phone(phone: str | None) -> str:
    """Format phone number to standard format.

    Args:
        phone: Phone number string

    Returns:
        Formatted phone number or empty string if None
    """
    if not phone:
        return ""

    # Remove any existing formatting
    cleaned = "".join(filter(str.isdigit, phone))

    if len(cleaned) == 10:
        return f"({cleaned[:3]})-{cleaned[3:6]}-{cleaned[6:]}"
    elif len(cleaned) == 11 and cleaned[0] == "1":
        return f"({cleaned[1:4]})-{cleaned[4:7]}-{cleaned[7:]}"

    # Return original if can't format
    return phone


def transform_user_to_resume_data(
    user_data: UserData,
    experience_data: list[Experience],
    responses: list[CandidateResponse],
    job_title: str,
) -> ResumeData:
    """Transform database data to ResumeData format.

    Args:
        user_data: UserData containing user, education, and certification data
        experience_data: List of user experiences
        responses: List of candidate responses
        job_title: Target job title for resume

    Returns:
        ResumeData object with all user information

    Raises:
        ValueError: If required user data is missing
    """
    user = user_data["user"]
    education_list = user_data["education"]
    certification_list = user_data["certifications"]

    # Validate required user data
    if not user.first_name or not user.last_name:
        raise ValueError("User must have first and last name")

    if not user.email:
        logger.warning(f"User {user.id} missing email address")
        user.email = "email@example.com"  # Placeholder for missing email

    # Transform education data
    resume_education = []
    for edu in education_list:
        resume_education.append(
            ResumeEducation(
                degree=edu.degree,
                major=edu.major,
                institution=edu.institution,
                grad_date=_format_date(edu.grad_date),
            )
        )

    # Transform certification data
    resume_certifications = []
    for cert in certification_list:
        resume_certifications.append(
            ResumeCertification(
                title=cert.title,
                date=_format_date(cert.date),
            )
        )

    # Transform experience data
    resume_experiences = []
    for exp in experience_data:
        resume_experiences.append(
            ResumeExperience(
                title=exp.title,
                company=exp.company,
                location=exp.location,
                start_date=_format_date(exp.start_date),
                end_date=_format_date(exp.end_date) if exp.end_date else "Present",
                points=[],  # Will be populated by experience bullet generation
            )
        )

    # Create ResumeData object
    resume_data = ResumeData(
        name=f"{user.first_name} {user.last_name}",
        title=job_title,
        email=user.email,
        phone=_format_phone(user.phone),
        linkedin_url=user.linkedin_url or "",
        professional_summary="",  # Will be populated by summary generation
        experience=resume_experiences,
        education=resume_education,
        skills=[],  # Will be populated by skills extraction
        certifications=resume_certifications,
    )

    return resume_data


def detect_missing_required_data(user_data: UserData) -> list[MissingRequiredField]:
    """Detect missing required data for resume generation.

    Args:
        user_data: UserData containing user, education, and certification data

    Returns:
        List of missing required field names
    """
    user = user_data["user"]
    missing_fields: list[MissingRequiredField] = []

    if not user.first_name:
        missing_fields.append("first_name")
    if not user.last_name:
        missing_fields.append("last_name")
    if not user.email:
        missing_fields.append("email")

    return missing_fields


def detect_missing_optional_data(
    user_data: UserData,
    experience_data: list[Experience],
    responses: list[CandidateResponse],
) -> list[MissingOptionalField]:
    """Detect missing optional data that would improve resume quality.

    Args:
        user_data: UserData containing user, education, and certification data
        experience_data: List of user experiences
        responses: List of candidate responses

    Returns:
        List of missing optional field names
    """
    user = user_data["user"]
    missing_fields: list[MissingOptionalField] = []

    if not user.phone:
        missing_fields.append("phone")
    if not user.linkedin_url:
        missing_fields.append("linkedin_url")
    if not user_data["education"]:
        missing_fields.append("education")
    if not experience_data:
        missing_fields.append("experience")
    if not responses:
        missing_fields.append("candidate_responses")

    return missing_fields
