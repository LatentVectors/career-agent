from typing import List, TypedDict

from pydantic.main import BaseModel

from .FileStorage import FileStorage
from .parse_interview_questions import InterviewQuestion
from .parse_motivations_and_interests import MotivationAndInterest


class Experience(BaseModel):
    title: str
    content: str


class Background(TypedDict):
    experience: List[Experience]
    motivations_and_interests: List[MotivationAndInterest]
    interview_questions: List[InterviewQuestion]


def get_background(storage: FileStorage) -> Background:
    """Get the background.

    This function reads the background from the file storage and returns it as a Background object.

    Args:
        storage: The file storage to read the background from.

    Returns:
        The background as a Background object.
    """
    experience: List[Experience] = []
    titles = storage.list_experience()
    for title in titles:
        content = storage.get_experience(title)
        experience.append(Experience(title=title.strip(".md"), content=content))

    motivations_and_interests = storage.get_motivations_and_interests()
    interview_questions = storage.get_interview_questions()

    return Background(
        experience=[e for e in experience if e.content.strip()],
        motivations_and_interests=[i for i in motivations_and_interests if i.answer.strip()],
        interview_questions=[i for i in interview_questions if i.answer],
    )
