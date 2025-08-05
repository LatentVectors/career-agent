from pydantic import BaseModel

JobRequirements = dict[int, str]


class RequirementSummary(BaseModel):
    """A summary of a requirement."""

    source: str
    """The source of the summary."""
    requirement: int
    """The requirement that the summary covers."""
    summary: str
    """A summary of the requirement."""
