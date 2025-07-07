import sys
from pathlib import Path

from loguru import logger


def setup_logging() -> None:
    """Configure loguru logging with three destinations.

    Sets up logging to:
    1. Console - human-readable messages only
    2. Human-readable log file with timestamps and metadata
    3. JSON log file for machine processing
    """
    # Remove default logger
    logger.remove()

    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # 1. Console output - clean, human-readable messages only
    logger.add(
        sys.stdout,
        format="{message}",
        colorize=True,
        level="INFO",
        filter=lambda record: record["level"].name in ["INFO", "WARNING", "ERROR", "CRITICAL"],
    )

    # 2. Human-readable log file with full metadata
    logger.add(
        logs_dir / "agentic.log",
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>",
        level="DEBUG",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
    )

    # 3. JSON log file for machine processing
    logger.add(
        logs_dir / "agentic.json",
        level="DEBUG",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        serialize=True,  # Let loguru handle JSON serialization
    )


# Initialize logging when module is imported
setup_logging()
