from __future__ import annotations

from typing import TypedDict

from pydantic import BaseModel

from src.db.models import CandidateResponse, Experience
from src.features.resume.data_adapter import UserData
from src.features.resume.types import ResumeData


class InputState(BaseModel):
    """The input state for the resume generator agent."""

    user_id: int
    """The user ID to generate resume for."""

    job_title: str
    """The target job title for the resume."""

    job_description: str
    """The full job description text to align resume content with."""


class OutputState(BaseModel):
    """The output state for the resume generator agent."""

    resume_text: str | None = None
    """The formatted string representation of the final resume."""

    resume_pdf_path: str | None = None
    """The path to the generated PDF resume."""

    page_length: int | None = None
    """The number of pages in the final resume."""

    optimization_feedback: str | None = None
    """Feedback about the optimization process."""


class ResumeGeneratorState(BaseModel):
    """Internal state for resume generation process."""

    # Input data
    user_data: UserData | None = None
    """User, education, and certification data."""

    experience_data: list[Experience] | None = None
    """User experience data."""

    responses_data: list[CandidateResponse] | None = None
    """Candidate response data."""

    # Resume data
    resume_data: ResumeData | None = None
    """The current resume data being processed."""

    # Page length tracking
    page_length: int = 0
    """Current page length of the resume."""

    optimization_attempts: int = 0
    """Number of optimization attempts made."""

    # Best option tracking
    best_resume_data: ResumeData | None = None
    """The best resume option found so far."""

    best_page_length: int | None = None
    """The page length of the best option."""

    best_pdf_path: str | None = None
    """The PDF path of the best option (draft or final)."""

    # Processing flags
    is_optimizing: bool = False
    """Whether currently in optimization mode."""

    # Feedback and logging
    optimization_feedback: str = ""
    """Feedback about the optimization process."""

    # Parallel processing tracking
    processed_experiences: list[int] | None = None
    """List of experience IDs that have been processed."""

    processed_responses: list[int] | None = None
    """List of response IDs that have been processed."""


class InternalState(InputState, OutputState, ResumeGeneratorState, BaseModel):
    """The complete state for the resume generator agent."""

    pass


class PartialInternalState(TypedDict, total=False):
    """The partial state for the resume generator agent."""

    user_id: int
    job_title: str
    job_description: str
    user_data: UserData | None
    experience_data: list[Experience] | None
    responses_data: list[CandidateResponse] | None
    resume_data: ResumeData | None
    page_length: int
    optimization_attempts: int
    best_resume_data: ResumeData | None
    best_page_length: int | None
    best_pdf_path: str | None
    is_optimizing: bool
    optimization_feedback: str
    processed_experiences: list[int] | None
    processed_responses: list[int] | None
    resume_text: str
    resume_pdf_path: str
