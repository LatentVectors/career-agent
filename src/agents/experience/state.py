from typing import Optional, TypedDict


class ExperienceInputState(TypedDict):
    """The input state for the experience agent."""

    job_description: str
    """The target job description."""

    experience: str
    """The work experience."""


class ExperienceOutputState(TypedDict):
    """The output state for the experience agent."""

    summary: str
    """The summary of the experience."""


class ExperienceState(TypedDict):
    """The state for the experience agent."""

    job_description: str
    """The target job description."""

    experience: str
    """The original experience."""

    summary: Optional[str]
    """The summary of the experience."""


class PartialExperienceState(TypedDict, total=False):
    """The partial state for the experience agent."""

    job_description: str
    experience: str
    summary: Optional[str]
