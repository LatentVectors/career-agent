from __future__ import annotations

from typing import List, TypedDict

from pydantic import BaseModel

from src.schemas import JobRequirements


class InputState(BaseModel):
    """The input state for the experience agent."""

    job_requirements: JobRequirements | None = None
    """The requirements for the job."""

    experience: str
    """The work experience."""


class OutputState(BaseModel):
    """The output state for the experience agent."""

    summary: List[ExperienceSummary] = []
    """The summary of the experience."""


class ExperienceSummary(BaseModel):
    """Summary of relevant experience."""

    requirement: List[int]
    """The related job requirements the experience aligns with. This must include at least one related requirement number."""

    summary: str
    """The summary of the experience."""


class InternalState(InputState, OutputState, BaseModel):
    """The state for the experience agent."""

    pass


class PartialInternalState(TypedDict, total=False):
    """The partial state for the experience agent."""

    job_requirements: JobRequirements | None
    experience: str | None
    summary: List[ExperienceSummary] | None
