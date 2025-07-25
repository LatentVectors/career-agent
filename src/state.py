from __future__ import annotations

from typing import Annotated, Dict, List, Optional, TypedDict

from .storage.get_background import Background, Experience
from .storage.parse_interview_questions import InterviewQuestion
from .storage.parse_job import Job
from .storage.parse_motivations_and_interests import MotivationAndInterest


def experience_reducer(a: Optional[dict], b: Optional[dict]) -> dict:
    """Reduce experience summaries."""
    if a is None:
        a = {}
    if b is not None:
        a.update(b)
    return a


class MainInputState(TypedDict):
    """Main input state."""

    job_description: str
    experience: List[Experience]
    motivations_and_interests: List[MotivationAndInterest]
    interview_questions: List[InterviewQuestion]


class MainOutputState(TypedDict):
    """Main output state."""

    cover_letter: Optional[str]
    """The cover letter."""

    resume: Optional[str]
    """The resume."""

    linkedin_message: Optional[str]
    """The LinkedIn message."""

    hr_manager_message: Optional[str]
    """The HR manager message."""

    hiring_manager_message: Optional[str]
    """The hiring manager message."""


class MainState(TypedDict, MainInputState, MainOutputState):
    """State."""

    current_experience_title: Optional[str]
    """The title of the current experience."""

    current_experience: Optional[str]
    """The current experience."""

    job_requirements: Optional[Dict[int, str]]
    """Extracted job requirements."""

    summarized_experience: Annotated[Optional[Dict[str, List[Summary]]], experience_reducer]
    """Summarized experience. The key is the title of the experience."""


class Summary(TypedDict):
    """Summary of the experience."""

    requirements: List[int]
    """The requirements that the summary covers."""

    summary: str
    """The summary of the experience."""


class PartialMainState(TypedDict, total=False):
    """Partial state for return types."""

    job_description: str
    experience: List[Experience]
    motivations_and_interests: List[MotivationAndInterest]
    interview_questions: List[InterviewQuestion]
    experience_summary: Optional[str]
    current_experience: Optional[str]
    current_experience_title: Optional[str]
    job_requirements: Optional[Dict[int, str]]
    cover_letter: Optional[str]
    resume: Optional[str]
    linkedin_message: Optional[str]
    hr_manager_message: Optional[str]
    hiring_manager_message: Optional[str]
    summarized_experience: Optional[Dict[str, List[Summary]]]


def get_main_input_state(
    job: Job,
    background: Background,
) -> MainInputState:
    """Get the state."""
    return MainInputState(
        job_description=job.description,
        motivations_and_interests=background["motivations_and_interests"],
        interview_questions=background["interview_questions"],
        experience=background["experience"],
    )
