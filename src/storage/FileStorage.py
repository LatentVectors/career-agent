from pathlib import Path
from typing import List

from .parse_interview_questions import InterviewQuestion, parse_interview_questions
from .parse_motivations_and_interests import MotivationAndInterest, parse_motivations_and_interests


class FileStorage:
    """File storage for the interview preparation tool.

    This class is responsible for saving and loading user-generated content related to employment.
    """

    def __init__(self, dir: Path) -> None:
        """Initialize the file storage.

        Args:
            dir: The directory to save the files to.
        """
        self._dir = dir
        if not self._dir.exists():
            self._dir.mkdir(parents=True, exist_ok=True)
        self._experience_dir = self._dir / "experience"

    def list_experience(self) -> List[str]:
        """List all experiences in the file storage."""
        return [f.name for f in self._experience_dir.glob("*.md")]

    def save_experience(self, filename: str, content: str) -> None:
        """Save an experience to the file storage.

        Args:
            filename: The name of the experience to save.
            content: The content of the experience to save.
        """
        if not filename.endswith(".md"):
            filename += ".md"
        filepath = self._experience_dir / filename
        if not filepath.exists():
            filepath.touch()
        with open(filepath, "a") as f:
            f.write(content)
            f.write("\n---\n")

    def load_experience(self, filename: str) -> str:
        """Load an experience from the file storage.

        Args:
            filename: The name of the experience to load.
        """
        filepath = self._experience_dir / filename
        if not filepath.exists():
            return ""
        with open(filepath, "r") as f:
            return f.read()

    def get_interview_questions(self) -> List[InterviewQuestion]:
        """Get the interview questions from the file storage."""
        filepath = self._dir / "interview_questions.md"
        if not filepath.exists():
            return []
        with open(filepath, "r") as f:
            content = f.read()
        return parse_interview_questions(content)

    def get_motivations_and_interests(self) -> List[MotivationAndInterest]:
        """Get the motivations and interests from the file storage."""
        filepath = self._dir / "motivations_and_interests.md"
        if not filepath.exists():
            return []
        with open(filepath, "r") as f:
            content = f.read()
        return parse_motivations_and_interests(content)
