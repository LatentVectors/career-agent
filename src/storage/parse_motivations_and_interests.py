import re
from typing import List

from src.schemas import MotivationAndInterest


def parse_motivations_and_interests(content: str) -> List[MotivationAndInterest]:
    """Parse the motivations and interests from the file storage.

    Args:
        content: The markdown content containing questions and answers.

    Returns:
        A list of MotivationAndInterest objects with parsed questions and answers.
    """
    # Split the content into sections based on lines starting with '#'
    sections = re.split(r"^#\s+", content, flags=re.MULTILINE)

    # Skip the first section if it's empty (content before first question)
    if sections and not sections[0].strip():
        sections = sections[1:]

    motivations_and_interests = []

    for section in sections:
        if not section.strip():
            continue

        # Split the section into lines
        lines = section.strip().split("\n")

        # The first line is the question
        question = lines[0].strip()

        # All remaining lines (after stripping empty lines) form the answer
        answer_lines = []
        for line in lines[1:]:
            line = line.strip()
            if line:  # Skip empty lines
                # Remove the leading dash and whitespace if present
                if line.startswith("-"):
                    line = line[1:].strip()
                answer_lines.append(line)

        # Join answer lines with spaces
        answer = " ".join(answer_lines)

        # Only add if we have both a question and an answer
        if question and answer:
            motivations_and_interests.append(
                MotivationAndInterest(question=question, answer=answer)
            )

    return motivations_and_interests
