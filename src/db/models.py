"""Persisted data models.

This module is exclusively for data that is persisted outside of the application.

This includes data that is stored in a database, files, or other external sources.

This module is not for data that is ephemeral or temporary.
"""

from __future__ import annotations

import datetime

from sqlmodel import Field as SQLField
from sqlmodel import SQLModel


class User(SQLModel, table=True):
    """Top-level personal information.

    Validation rules:
    • *email* – must be a valid e-mail address when non-empty.
    • *phone* – ``(###)-###-####`` when non-empty.
    • *linkedin_url* – valid URL which includes the domain *linkedin.com* when non-empty.
    """

    id: int = SQLField(default=None, primary_key=True)
    first_name: str = SQLField(..., description="First name")
    last_name: str = SQLField(..., description="Last name")
    # TODO: This should include more granular validation.
    email: str | None = SQLField(
        None,
        description="Email address",
        sa_column_kwargs={"unique": True},
    )
    # TODO: This should be stored in a different format so I can more flexibly format it.
    # TODO: Can this be a tuple of specific length integers, or should it be a special object with specific strings?
    phone: str | None = SQLField(
        None,
        description="Phone number – (###)-###-####",
    )
    linkedin_url: str | None = SQLField(
        None,
        description="LinkedIn profile URL",
    )
    created_at: datetime.datetime = SQLField(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = SQLField(default_factory=datetime.datetime.now)

    @property
    def full_name(self) -> str:
        """Return the full name of the user."""
        return f"{self.first_name} {self.last_name}"


class Education(SQLModel, table=True):
    """Education information for a resume."""

    id: int = SQLField(default=None, primary_key=True)
    user_id: int = SQLField(foreign_key="user.id")
    degree: str = SQLField(..., description="The degree obtained")
    major: str = SQLField(..., description="The field of study")
    institution: str = SQLField(..., description="The educational institution")
    grad_date: datetime.date = SQLField(..., description="Graduation date")
    created_at: datetime.datetime = SQLField(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = SQLField(default_factory=datetime.datetime.now)


class Certification(SQLModel, table=True):
    """Certification information for a resume."""

    id: int = SQLField(default=None, primary_key=True)
    user_id: int = SQLField(foreign_key="user.id")
    title: str = SQLField(..., description="The certification title")
    date: datetime.date = SQLField(..., description="The date the certification was obtained")
    created_at: datetime.datetime = SQLField(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = SQLField(default_factory=datetime.datetime.now)


class Experience(SQLModel, table=True):
    """Work experience information for a resume."""

    id: int = SQLField(default=None, primary_key=True)
    user_id: int = SQLField(foreign_key="user.id")
    title: str = SQLField(..., description="Job title")
    company: str = SQLField(..., description="Company name")
    location: str = SQLField(..., description="Job location")
    start_date: datetime.date = SQLField(..., description="Start date of employment")
    end_date: datetime.date | None = SQLField(
        None, description="End date of employment (or 'Present')"
    )
    content: str = SQLField(..., description="The candidate's experience.")
    created_at: datetime.datetime = SQLField(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = SQLField(default_factory=datetime.datetime.now)


class Company(SQLModel, table=True):
    """Company data structure."""

    id: int = SQLField(default=None, primary_key=True)
    name: str = SQLField(..., unique=True)
    website: str | None = None
    email: str | None = None
    overview: str | None = None
    created_at: datetime.datetime = SQLField(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = SQLField(default_factory=datetime.datetime.now)


class JobPosting(SQLModel, table=True):
    """Job posting data structure."""

    id: int = SQLField(default=None, primary_key=True)
    company_id: int = SQLField(foreign_key="company.id")
    description: str = SQLField(..., description="Job description")
    requirements: str = SQLField(default="{}", description="Numbered requirements as JSON string.")
    keywords: str = SQLField(default="{}", description="Keyword and their counts as JSON string.")
    created_at: datetime.datetime = SQLField(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = SQLField(default_factory=datetime.datetime.now)


class Comment(SQLModel, table=True):
    """Comment data structure."""

    id: int = SQLField(default=None, primary_key=True)
    text: str = SQLField(..., description="The comment text.")
    created_at: datetime.datetime = SQLField(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = SQLField(default_factory=datetime.datetime.now)

    # Polymorphic relationships
    job_posting_id: int | None = SQLField(foreign_key="jobposting.id", default=None)
    company_id: int | None = SQLField(foreign_key="company.id", default=None)


class CandidateResponse(SQLModel, table=True):
    """Candidate response data structure."""

    id: int = SQLField(default=None, primary_key=True)
    user_id: int = SQLField(foreign_key="user.id")
    prompt: str = SQLField(..., description="The prompt that the candidate responded to.")
    response: str = SQLField(..., description="The candidate's response.")
    created_at: datetime.datetime = SQLField(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = SQLField(default_factory=datetime.datetime.now)
