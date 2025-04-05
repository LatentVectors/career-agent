import sys
from pathlib import Path

from loguru import logger
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

logger.remove()
logger.add(sys.stdout, format="{message}", colorize=True, level="INFO")
logger.add("logs/agentic.log", level="DEBUG", rotation="10 MB")

PROJECT_ROOT = Path(__file__).parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"


class Settings(BaseSettings):
    openai_api_key: SecretStr

    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", env_file_encoding="utf-8")


# Don't worry about a type error here, it should load the variable from the .env file
SETTINGS = Settings()  # type: ignore

logger.debug(f"Project root: {PROJECT_ROOT}")
