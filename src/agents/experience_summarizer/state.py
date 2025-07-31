from __future__ import annotations

from typing import List, Optional, TypedDict

from src.types import JobRequirements


class ExperienceInputState(TypedDict):
    """The input state for the experience agent."""

    job_requirements: Optional[JobRequirements]
    """The requirements for the job."""

    experience: str
    """The work experience."""


class ExperienceOutputState(TypedDict):
    """The output state for the experience agent."""

    summary: Optional[List[ExperienceSummary]]
    """The summary of the experience."""


class ExperienceSummary(TypedDict):
    """Summary of relevant experience."""

    requirement: List[int]
    """The related job requirements the experience aligns with. This must include at least one related requirement number."""

    summary: str
    """The summary of the experience."""


class ExperienceState(TypedDict):
    """The state for the experience agent."""

    job_description: str
    """The target job description."""

    job_requirements: Optional[JobRequirements]
    """The requirements for the job."""

    experience: str
    """The original experience."""

    matches: Optional[str]
    """The matches between the job description and the experience."""

    summary: Optional[List[ExperienceSummary]]
    """The summary of the experience."""


# NOTE: PartialExperienceState should mirror ExperienceState.
class PartialExperienceState(TypedDict, total=False):
    """The partial state for the experience agent."""

    job_description: str
    job_requirements: Optional[JobRequirements]
    experience: str
    matches: Optional[str]
    summary: Optional[List[ExperienceSummary]]
