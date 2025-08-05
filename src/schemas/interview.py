from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class InterviewQuestion(BaseModel):
    """Interview question data structure."""

    question: str
    category: Optional[str] = None
    answer: Optional[str] = None
    motivation: Optional[str] = None
    guidance: Optional[str] = None
    notes: Optional[str] = None
