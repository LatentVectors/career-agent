from typing import List

from pydantic import BaseModel


class RequirementSummary(BaseModel):
    """Summary of a requirement."""

    source: str
    """The source document the summary is from."""

    requirements: List[int]
    """The job requirements that the summary covers."""

    summary: str
    """The summary of the requirement."""
