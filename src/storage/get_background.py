"""Aggregate user background information for the agent pipeline."""

from __future__ import annotations

from typing import List

from src.schemas import Background, BackgroundExperience

from .FileStorage import FileStorage
from .parse_experience import parse_experience_file


def get_background(storage: FileStorage) -> Background:
    """Return all persisted background information in a single object.

    This function reads the background from the file storage and returns it as a Background object.

    Args:
        storage: The file storage to read the background from.

    Returns:
        The background as a Background object.
    """
    experience: List[BackgroundExperience] = []
    for filename in storage.list_experience():
        raw_content = storage.get_experience(filename)
        exp_meta, body = parse_experience_file(raw_content)
        experience.append(
            BackgroundExperience(
                title=exp_meta.title or filename.strip(".md"),
                content=body,
            )
        )

    motivations_and_interests = storage.get_motivations_and_interests()
    interview_questions = storage.get_interview_questions()

    return Background(
        experience=[e for e in experience if e.content.strip()],
        motivations_and_interests=[i for i in motivations_and_interests if i.answer.strip()],
        interview_questions=[i for i in interview_questions if i.answer],
    )
