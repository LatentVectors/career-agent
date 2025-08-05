from __future__ import annotations

from pydantic import BaseModel


class MotivationAndInterest(BaseModel):
    """Motivation and interest data structure."""

    question: str
    answer: str
