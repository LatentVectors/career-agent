from typing import Dict, List

from pydantic import BaseModel

JobRequirements = Dict[int, str]


class CandidateResponse(BaseModel):
    """A response from a candidate."""

    prompt: str
    """The prompt provided to the candidate."""

    response: str
    """The response from the candidate."""


class RequirementSummary(BaseModel):
    """Summary of a requirement."""

    source: str
    """The source document the summary is from."""

    requirements: List[int]
    """The job requirements that the summary covers."""

    summary: str
    """The summary of the requirement."""
