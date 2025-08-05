from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class Job(BaseModel):
    """Job posting data structure."""

    company_name: str
    description: str
    company_website: Optional[str] = None
    company_email: Optional[str] = None
    company_overview: Optional[str] = None
    parsed_requirements: Optional[List[str]] = None
    my_interest: Optional[str] = None
    cover_letter: Optional[str] = None
