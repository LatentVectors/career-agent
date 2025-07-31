from typing import TypedDict

from src.types import CandidateResponse, JobRequirements, RequirementSummary


class ResponsesInputState(TypedDict):
    """Input state for the responses summarizer."""

    source: str
    """The source of the responses."""

    responses: list[CandidateResponse]
    """A list of responses from the candidate."""

    job_requirements: JobRequirements
    """The job requirements."""


class ResponsesOutputState(TypedDict):
    """Output state for the responses summarizer."""

    summaries: list[RequirementSummary]
    """A list of summaries of the responses."""


class ResponsesState(TypedDict, ResponsesInputState, ResponsesOutputState):
    """State for the responses summarizer."""

    pass


# NOTE: The this should match the ResponsesState but with total=False.
class PartialResponsesState(TypedDict, total=False):
    responses: list[CandidateResponse]
    summaries: list[RequirementSummary]
