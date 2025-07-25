from pathlib import Path

import pytest
from src.storage.parse_motivations_and_interests import (
    MotivationAndInterest,
    parse_motivations_and_interests,
)


def test_parse_motivations_and_interests():
    """Test parsing motivations and interests from markdown content."""
    # Test with a simple example
    content = """# What is your favorite color?
    - Blue is my favorite color because it reminds me of the ocean.
    - I also like green for nature.

# What do you enjoy doing?
    - I enjoy reading books.
    - I love hiking in the mountains."""

    result = parse_motivations_and_interests(content)

    assert len(result) == 2
    assert result[0].prompt == "What is your favorite color?"
    assert "Blue is my favorite color" in result[0].answer
    assert result[1].prompt == "What do you enjoy doing?"
    assert "I enjoy reading books" in result[1].answer


def test_parse_motivations_and_interests_with_empty_sections():
    """Test parsing with empty sections and questions without answers."""
    content = """# Question with answer
    - This is an answer.

# Question without answer

# Another question with answer
    - Another answer."""

    result = parse_motivations_and_interests(content)

    assert len(result) == 2  # Should skip the question without answer
    assert result[0].prompt == "Question with answer"
    assert result[1].prompt == "Another question with answer"


def test_parse_motivations_and_interests_with_real_data():
    """Test parsing with actual data from the markdown file."""
    data_file = Path("data/motivations_and_interests.md")
    if not data_file.exists():
        pytest.skip("Data file not found")

    content = data_file.read_text()
    result = parse_motivations_and_interests(content)

    # Should have multiple parsed items
    assert len(result) > 0

    # Check that we have valid questions and answers
    for item in result:
        assert isinstance(item, MotivationAndInterest)
        assert item.prompt.strip()
        assert item.answer.strip()
        # Questions should not start with '#'
        assert not item.prompt.startswith("#")
        # Answers should not start with '-'
        assert not item.answer.startswith("-")


def test_parse_motivations_and_interests_edge_cases():
    """Test parsing with edge cases."""
    # Empty content
    result = parse_motivations_and_interests("")
    assert result == []

    # Content with no questions
    result = parse_motivations_and_interests("Just some text without questions.")
    assert result == []

    # Content with only questions, no answers
    result = parse_motivations_and_interests("# Question 1\n# Question 2")
    assert result == []
