from typing import Dict, Optional, TypedDict


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

    job_requirements: Optional[Dict[str, str]]
    """The requirements for the job."""

    experience: str
    """The original experience."""

    matches: Optional[str]
    """The matches between the job description and the experience."""

    summary: Optional[str]
    """The summary of the experience."""


# NOTE: PartialExperienceState should mirror ExperienceState.
class PartialExperienceState(TypedDict, total=False):
    """The partial state for the experience agent."""

    job_description: str
    job_requirements: Optional[Dict[str, str]]
    experience: str
    matches: Optional[str]
    summary: Optional[str]
