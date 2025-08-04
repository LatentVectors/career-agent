from __future__ import annotations

from typing import Annotated, Dict, List, Optional, TypedDict

from pydantic import BaseModel

from .storage.get_background import Background, Experience
from .storage.parse_interview_questions import InterviewQuestion
from .storage.parse_job import Job
from .storage.parse_motivations_and_interests import MotivationAndInterest


def dict_reducer(a: Optional[dict], b: Optional[dict]) -> dict:
    """Reduce a dictionary using keys to merge the values."""
    if a is None:
        a = {}
    if b is not None:
        a.update(b)
    return a


class InputState(BaseModel):
    """Main input state."""

    job_description: str
    experience: List[Experience]
    motivations_and_interests: List[MotivationAndInterest]
    interview_questions: List[InterviewQuestion]


class OutputState(BaseModel):
    """Main output state."""

    cover_letter: str | None = None
    """The cover letter."""

    resume: str | None = None
    """The resume."""

    linkedin_message: str | None = None
    """The LinkedIn message."""

    hr_manager_message: str | None = None
    """The HR manager message."""

    hiring_manager_message: str | None = None
    """The hiring manager message."""


class InternalState(InputState, OutputState, BaseModel):
    """State."""

    current_experience_title: str | None = None
    """The title of the current experience."""

    current_experience: str | None = None
    """The current experience."""

    job_requirements: Dict[int, str] = {}
    """Extracted job requirements."""

    summarized_experience: Annotated[Dict[str, List[Summary]], dict_reducer] = {}
    """Summarized experience. The key is the title of the experience."""

    summarized_responses: Annotated[Dict[str, List[Summary]], dict_reducer] = {}
    """Summarized responses. The key is the source of the responses."""

    cover_letter_feedback: str | None = None
    """Feedback for the cover letter."""


class Summary(BaseModel):
    """Summary of the experience."""

    requirements: List[int]
    """The requirements that the summary covers."""

    summary: str
    """The summary of the experience."""


class PartialInternalState(TypedDict, total=False):
    """Partial state for return types."""

    job_description: str | None
    experience: List[Experience] | None
    motivations_and_interests: List[MotivationAndInterest] | None
    interview_questions: List[InterviewQuestion] | None
    experience_summary: str | None
    current_experience: str | None
    current_experience_title: str | None
    job_requirements: Dict[int, str] | None
    cover_letter: str | None
    resume: str | None
    linkedin_message: str | None
    hr_manager_message: str | None
    hiring_manager_message: str | None
    summarized_experience: Dict[str, List[Summary]] | None
    summarized_responses: Dict[str, List[Summary]] | None
    cover_letter_feedback: str | None


def get_main_input_state(
    job: Job,
    background: Background,
) -> InputState:
    """Get the state."""
    return InternalState(
        job_description=job.description,
        motivations_and_interests=background["motivations_and_interests"],
        interview_questions=background["interview_questions"],
        experience=background["experience"],
    )
