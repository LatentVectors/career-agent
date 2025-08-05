"""Data schemas for the application."""

from .application import CandidateResponse, JobRequirements, RequirementSummary
from .background import Background
from .background import Experience as BackgroundExperience
from .interview import InterviewQuestion
from .job import Job
from .motivation import MotivationAndInterest
from .resume import (
    Certification,
    Education,
    ResumeData,
    UserProfile,
)
from .resume import (
    Experience as ResumeExperience,
)

__all__ = [
    # Application models
    "CandidateResponse",
    "JobRequirements",
    "RequirementSummary",
    # Background models
    "Background",
    "BackgroundExperience",
    # Interview models
    "InterviewQuestion",
    # Job models
    "Job",
    # Motivation models
    "MotivationAndInterest",
    # Resume models
    "Certification",
    "Education",
    "ResumeExperience",
    "ResumeData",
    "UserProfile",
]
