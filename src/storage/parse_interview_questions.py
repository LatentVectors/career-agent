import re
from typing import List, Optional

from src.schemas import InterviewQuestion


def parse_interview_questions(content: str) -> List[InterviewQuestion]:
    """Parse the interview questions from the file storage.

    Args:
        content: The markdown content containing interview questions.

    Returns:
        A list of InterviewQuestion objects parsed from the content.
    """
    questions: List[InterviewQuestion] = []

    # Split content by question headers (lines starting with #)
    sections = re.split(r"^#\s+", content, flags=re.MULTILINE)

    for i, section in enumerate(sections):
        if not section.strip():
            continue

        lines = section.strip().split("\n")
        if not lines:
            continue

        # First line is the question
        question_text = lines[0].strip()
        if not question_text:
            continue

        # Skip the first section if it doesn't start with # (content before first question)
        if i == 0 and not content.strip().startswith("#"):
            continue

        # Parse the rest of the section for fields
        current_field = None
        field_content: List[str] = []
        question_data: dict[str, Optional[str]] = {
            "question": question_text,
            "category": None,
            "answer": None,
            "motivation": None,
            "guidance": None,
            "notes": None,
        }

        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue

            # Check if this is a field header
            field_match = re.match(r"^\*\*(.+?)\*\*$", line)
            if field_match:
                # Save previous field content
                if current_field:
                    content_text = "\n".join(field_content).strip() if field_content else ""
                    if current_field.lower() == "category":
                        question_data["category"] = content_text
                    elif current_field.lower() == "response":
                        question_data["answer"] = content_text
                    elif current_field.lower() == "motivation":
                        question_data["motivation"] = content_text
                    elif current_field.lower() == "guidance":
                        question_data["guidance"] = content_text
                    elif current_field.lower() == "notes":
                        question_data["notes"] = content_text

                # Start new field
                current_field = field_match.group(1)
                field_content = []
            else:
                # Add line to current field content
                if current_field:
                    field_content.append(line)

        # Save the last field content
        if current_field:
            content_text = "\n".join(field_content).strip() if field_content else ""
            if current_field.lower() == "category":
                question_data["category"] = content_text
            elif current_field.lower() == "response":
                question_data["answer"] = content_text
            elif current_field.lower() == "motivation":
                question_data["motivation"] = content_text
            elif current_field.lower() == "guidance":
                question_data["guidance"] = content_text
            elif current_field.lower() == "notes":
                question_data["notes"] = content_text

        # Create InterviewQuestion object
        question = InterviewQuestion(
            question=question_data["question"] or "",
            category=question_data["category"],
            answer=question_data["answer"],
            motivation=question_data["motivation"],
            guidance=question_data["guidance"],
            notes=question_data["notes"],
        )
        questions.append(question)

    return questions
