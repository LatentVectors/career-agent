from pathlib import Path

import pytest
from src.storage.parse_interview_questions import parse_interview_questions


class TestParseInterviewQuestions:
    """Test cases for parse_interview_questions function."""

    def test_parse_single_question_with_all_fields(self):
        """Test parsing a single question with all fields populated."""
        content = """# Tell me about yourself.
**Category**
Questions About You and Your Motivation

**Motivation**
This is a warm-up and a test of your communication skills.

**Guidance**
Use the **"Present-Past-Future"** formula.

**Notes**
- Currently, I am an entrepreneur.
- Previously, I worked at Rimports.

**Response**
- I'm a data analyst with over 6 years experience.
- Recently, I've been validating new product opportunities."""

        result = parse_interview_questions(content)

        assert len(result) == 1
        question = result[0]
        assert question.question == "Tell me about yourself."
        assert question.category == "Questions About You and Your Motivation"
        assert question.motivation == "This is a warm-up and a test of your communication skills."
        assert question.guidance == 'Use the **"Present-Past-Future"** formula.'
        assert (
            question.notes
            == "- Currently, I am an entrepreneur.\n- Previously, I worked at Rimports."
        )
        assert (
            question.answer
            == "- I'm a data analyst with over 6 years experience.\n- Recently, I've been validating new product opportunities."
        )

    def test_parse_multiple_questions(self):
        """Test parsing multiple questions."""
        content = """# First question?
**Category**
Category 1

**Response**
Answer 1

# Second question?
**Category**
Category 2

**Response**
Answer 2"""

        result = parse_interview_questions(content)

        assert len(result) == 2
        assert result[0].question == "First question?"
        assert result[0].category == "Category 1"
        assert result[0].answer == "Answer 1"
        assert result[1].question == "Second question?"
        assert result[1].category == "Category 2"
        assert result[1].answer == "Answer 2"

    def test_parse_question_with_missing_fields(self):
        """Test parsing a question with some fields missing."""
        content = """# Simple question?
**Category**
Test Category

**Response**
Test Answer"""

        result = parse_interview_questions(content)

        assert len(result) == 1
        question = result[0]
        assert question.question == "Simple question?"
        assert question.category == "Test Category"
        assert question.answer == "Test Answer"
        assert question.motivation is None
        assert question.guidance is None
        assert question.notes is None

    def test_parse_question_with_multiline_content(self):
        """Test parsing a question with multiline content in fields."""
        content = """# Complex question?
**Category**
Multi-line Category
with extra content

**Motivation**
This is a multi-line
motivation field
with multiple lines

**Response**
This is a multi-line
response with
multiple lines of content"""

        result = parse_interview_questions(content)

        assert len(result) == 1
        question = result[0]
        assert question.question == "Complex question?"
        assert question.category == "Multi-line Category\nwith extra content"
        assert question.motivation == "This is a multi-line\nmotivation field\nwith multiple lines"
        assert question.answer == "This is a multi-line\nresponse with\nmultiple lines of content"

    def test_parse_empty_content(self):
        """Test parsing empty content."""
        result = parse_interview_questions("")
        assert result == []

    def test_parse_content_with_no_questions(self):
        """Test parsing content that doesn't contain any questions."""
        content = """This is just some text
without any question headers.

**Category**
This won't be parsed as a question."""

        result = parse_interview_questions(content)
        assert result == []

    def test_parse_question_with_empty_fields(self):
        """Test parsing a question with empty field content."""
        content = """# Question with empty fields?
**Category**

**Motivation**

**Response**"""

        result = parse_interview_questions(content)

        assert len(result) == 1
        question = result[0]
        assert question.question == "Question with empty fields?"
        assert question.category == ""
        assert question.motivation == ""
        assert question.answer == ""

    def test_parse_real_interview_questions_file(self):
        """Test parsing the actual interview questions markdown file."""
        file_path = Path("data/interview_questions.md")
        if not file_path.exists():
            pytest.skip("Interview questions file not found")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        result = parse_interview_questions(content)

        # Should parse multiple questions
        assert len(result) > 0

        # Check that first question is parsed correctly
        first_question = result[0]
        assert first_question.question == "Tell me about yourself."
        assert first_question.category == "Questions About You and Your Motivation"
        assert first_question.motivation is not None
        assert first_question.guidance is not None
        assert first_question.notes is not None
        assert first_question.answer is not None

        # Check that all questions have required fields
        for question in result:
            assert question.question is not None
            assert question.question != ""

    def test_parse_question_with_special_characters(self):
        """Test parsing a question with special characters in field content."""
        content = """# Question with special chars?
**Category**
Category with **bold** and *italic* text

**Motivation**
Motivation with "quotes" and 'apostrophes'

**Response**
Response with:
- Bullet points
- More bullets
- And **bold** text"""

        result = parse_interview_questions(content)

        assert len(result) == 1
        question = result[0]
        assert question.question == "Question with special chars?"
        assert question.category == "Category with **bold** and *italic* text"
        assert question.motivation == "Motivation with \"quotes\" and 'apostrophes'"
        assert (
            question.answer
            == "Response with:\n- Bullet points\n- More bullets\n- And **bold** text"
        )

    def test_parse_question_with_whitespace(self):
        """Test parsing a question with various whitespace patterns."""
        content = """#   Question with extra whitespace?   
**Category**
   Category with leading spaces   
**Motivation**
Motivation with trailing spaces   
**Response**
   Response with mixed whitespace   """

        result = parse_interview_questions(content)

        assert len(result) == 1
        question = result[0]
        assert question.question == "Question with extra whitespace?"
        assert question.category == "Category with leading spaces"
        assert question.motivation == "Motivation with trailing spaces"
        assert question.answer == "Response with mixed whitespace"
