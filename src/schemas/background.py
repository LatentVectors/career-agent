from __future__ import annotations

from typing import List, TypedDict

from pydantic import BaseModel

from .interview import InterviewQuestion
from .motivation import MotivationAndInterest


class Experience(BaseModel):
    """Background experience data structure."""

    title: str
    content: str


class Background(TypedDict):
    """Aggregated background information."""

    experience: List[Experience]
    motivations_and_interests: List[MotivationAndInterest]
    interview_questions: List[InterviewQuestion]
