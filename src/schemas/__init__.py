from pydantic import BaseModel

JobRequirements = dict[int, str]


class RequirementSummary(BaseModel):
    """A summary of a requirement."""

    source: str
    """The source of the summary."""
    requirements: list[int]
    """The requirements that the summary covers."""
    summary: str
    """A summary of the requirement."""
