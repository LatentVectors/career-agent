"""Filesystem-backed persistence layer.

This module grew a few additional responsibilities:
* Store and retrieve a *user profile* in JSON form.
* Read/write experience Markdown files that contain YAML front-matter so that
  structured metadata can be captured alongside the free-text content.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from src.schemas import (
    InterviewQuestion,
    Job,
    MotivationAndInterest,
    ResumeExperience,
    UserProfile,
)
from src.storage.parse_experience import format_experience, parse_experience_file
from src.storage.parse_job import format_job, parse_job

from .parse_interview_questions import parse_interview_questions
from .parse_motivations_and_interests import parse_motivations_and_interests


class FileStorage:  # noqa: D101 – docstring below
    """Filesystem abstraction used throughout the project."""

    PROFILE_FILE_NAME = "user_profile.json"

    def __init__(self, dir: Path) -> None:
        """Initialize the file storage.

        Args:
            dir: The directory to save the files to.
        """
        self._dir = dir
        self._dir.mkdir(parents=True, exist_ok=True)

        # Sub-directories ----------------------------------------------------
        self._experience_dir = self._dir / "experience"
        self._jobs_dir = self._dir / "jobs"
        self._experience_dir.mkdir(parents=True, exist_ok=True)
        self._jobs_dir.mkdir(parents=True, exist_ok=True)

        # Profile path -------------------------------------------------------
        self._profile_file = self._dir / self.PROFILE_FILE_NAME

    # ---------------------------------------------------------------------
    # Experience helpers
    # ---------------------------------------------------------------------
    def list_experience(self) -> List[str]:
        """List all experiences in the file storage."""
        return [f.name for f in self._experience_dir.glob("*.md")]

    def save_experience(
        self, experience_or_filename: ResumeExperience | str, content: str
    ) -> None:  # noqa: D401
        """Save an experience.

        Backwards-compatibility: When *experience_or_filename* is a string we
        treat it as a *filename* and write *content* verbatim (legacy path).
        When it is an :class:`Experience` we render YAML front-matter before
        writing the file so that structured metadata is preserved.
        """

        if isinstance(experience_or_filename, ResumeExperience):
            exp = experience_or_filename
            filename = f"{exp.title}.md"
            formatted = format_experience(exp, content)
        else:
            # Legacy behaviour – no YAML front-matter.
            filename = (
                experience_or_filename
                if experience_or_filename.endswith(".md")
                else f"{experience_or_filename}.md"
            )
            formatted = content

        filepath = self._experience_dir / filename
        filepath.write_text(formatted)

    def get_experience(self, filename: str) -> str:
        """Load an experience from the file storage.

        Args:
            filename: The name of the experience to load.
        """
        filepath = self._experience_dir / filename
        if not filepath.exists():
            return ""
        return filepath.read_text()

    # High-level convenience: parse experience and return model -------------
    def get_experience_metadata(self, filename: str) -> ResumeExperience:
        """Return the :class:`Experience` metadata embedded in *filename*."""

        content = self.get_experience(filename)
        exp, _body = parse_experience_file(content)
        return exp

    def get_interview_questions(self) -> List[InterviewQuestion]:
        """Get the interview questions from the file storage."""
        filepath = self._dir / "interview_questions.md"
        if not filepath.exists():
            return []
        content = filepath.read_text()
        return parse_interview_questions(content)

    def get_motivations_and_interests(self) -> List[MotivationAndInterest]:
        """Get the motivations and interests from the file storage."""
        filepath = self._dir / "motivations_and_interests.md"
        if not filepath.exists():
            return []
        content = filepath.read_text()
        return parse_motivations_and_interests(content)

    def job_exists(self, company_name: str) -> bool:
        """Check if a job exists in the file storage."""
        if not company_name.endswith(".md"):
            company_name += ".md"
        return (self._jobs_dir / company_name).exists()

    def list_jobs(self) -> List[str]:
        """List all jobs in the file storage."""
        return [f.name for f in self._jobs_dir.glob("*.md")]

    def get_job(self, company_name: str) -> Job:
        """Get a job from the file storage."""
        if not company_name.endswith(".md"):
            company_name += ".md"
        filepath = self._jobs_dir / company_name
        if not filepath.exists():
            raise FileNotFoundError(f"Job {company_name} not found")
        return parse_job(filepath.read_text())

    def save_job(self, job: Job) -> None:
        """Save a job to the file storage."""
        filepath = self._jobs_dir / f"{job.company_name}.md"
        filepath.write_text(format_job(job))

    # ---------------------------------------------------------------------
    # User profile helpers
    # ---------------------------------------------------------------------
    def get_user_profile(self) -> UserProfile:
        """Return the stored :class:`UserProfile` (empty profile if none)."""

        if not self._profile_file.exists():
            return UserProfile(name="", email="", phone="", linkedin_url="")
        data = json.loads(self._profile_file.read_text())
        return UserProfile.model_validate(data)

    def save_user_profile(self, profile: UserProfile) -> None:
        """Persist *profile* to disk (JSON)."""

        self._profile_file.write_text(json.dumps(profile.model_dump(mode="json"), indent=2))
