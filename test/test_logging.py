"""Test logging configuration."""

import json
from pathlib import Path

# Import the logging configuration to ensure it's set up
from src.logging_config import logger


def test_logging_configuration() -> None:
    """Test that logging is configured with all three destinations."""
    # Test different log levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    # Test with extra context
    logger.bind(user_id="123", action="test").info("Message with context")

    # Test exception logging
    try:
        raise ValueError("Test exception")
    except ValueError:
        logger.exception("Caught an exception")
        # Don't re-raise the exception for clean test execution

    # Verify files were created
    logs_dir = Path("logs")
    assert logs_dir.exists(), "Logs directory should exist"

    human_log = logs_dir / "agentic.log"
    json_log = logs_dir / "agentic.json"

    assert human_log.exists(), "Human-readable log file should exist"
    assert json_log.exists(), "JSON log file should exist"

    # Verify JSON log contains valid JSON
    with open(json_log, "r") as f:
        for line in f:
            if line.strip():
                try:
                    json.loads(line)
                except json.JSONDecodeError:
                    assert False, f"Invalid JSON in log file: {line}"


if __name__ == "__main__":
    test_logging_configuration()
    print("✅ Logging configuration test passed!")
