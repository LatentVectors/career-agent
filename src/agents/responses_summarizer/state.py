from typing import TypedDict

from pydantic import BaseModel

from src.schemas import CandidateResponse, JobRequirements, RequirementSummary


class InputState(BaseModel):
    """Input state for the responses summarizer."""

    source: str
    """The source of the responses."""

    responses: list[CandidateResponse]
    """A list of responses from the candidate."""

    job_requirements: JobRequirements
    """The job requirements."""


class OutputState(BaseModel):
    """Output state for the responses summarizer."""

    summaries: list[RequirementSummary] = []
    """A list of summaries of the responses."""


class InternalState(InputState, OutputState, BaseModel):
    """State for the responses summarizer."""

    pass


class PartialInternalState(TypedDict, total=False):
    source: str | None
    responses: list[CandidateResponse] | None
    job_requirements: JobRequirements | None
    summaries: list[RequirementSummary] | None
