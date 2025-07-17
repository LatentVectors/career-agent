from typing import Annotated, List, Optional, TypedDict

from .storage.get_background import Background, Experience
from .storage.parse_interview_questions import InterviewQuestion
from .storage.parse_job import Job
from .storage.parse_motivations_and_interests import MotivationAndInterest


def experience_reducer(a: str, b: str) -> str:
    """Reduce experience summaries."""
    if b is None or b.strip() == "":
        return a
    if a is None or a.strip() == "":
        return b
    if b in a:
        return a
    return f"{a}\n\n---\n\n{b}"


class MainInputState(TypedDict):
    """Main input state."""

    # Job
    company_name: str
    job_description: str
    company_website: Optional[str]
    company_email: Optional[str]
    company_overview: Optional[str]
    my_interest: Optional[str]
    cover_letter: Optional[str]

    # Background
    experience: List[Experience]
    motivations_and_interests: List[MotivationAndInterest]
    interview_questions: List[InterviewQuestion]


class MainOutputState(TypedDict):
    """Main output state."""

    experience_summary: Optional[str]


class MainState(TypedDict):
    """State."""

    # Job
    company_name: str
    job_description: str
    company_website: Optional[str]
    company_email: Optional[str]
    company_overview: Optional[str]
    my_interest: Optional[str]
    cover_letter: Optional[str]

    # Background
    experience: List[Experience]
    motivations_and_interests: List[MotivationAndInterest]
    interview_questions: List[InterviewQuestion]

    # Experience Summary
    current_experience: Optional[Experience]
    experience_summary: Annotated[Optional[str], experience_reducer]


class PartialMainState(TypedDict, total=False):
    """Partial state for return types."""

    # Job
    company_name: str
    job_description: str
    company_website: Optional[str]
    company_email: Optional[str]
    company_overview: Optional[str]
    my_interest: Optional[str]
    cover_letter: Optional[str]

    # Background
    experience: List[Experience]
    motivations_and_interests: List[MotivationAndInterest]
    interview_questions: List[InterviewQuestion]

    # Experience Summary
    experience_summary: Optional[str]


def get_main_input_state(
    job: Job,
    background: Background,
) -> MainInputState:
    """Get the state."""
    return MainInputState(
        company_name=job.company_name,
        job_description=job.description,
        company_website=job.company_website,
        company_email=job.company_email,
        company_overview=job.company_overview,
        my_interest=job.my_interest,
        cover_letter=job.cover_letter,
        motivations_and_interests=background["motivations_and_interests"],
        interview_questions=background["interview_questions"],
        experience=background["experience"],
    )
