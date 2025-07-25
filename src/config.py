from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Import logging configuration
from .logging_config import logger

PROJECT_ROOT = Path(__file__).parent.parent

DATA_DIR = PROJECT_ROOT / "data"
if not DATA_DIR.exists():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

CASSETTE_DIR = DATA_DIR / "cassettes"
if not CASSETTE_DIR.exists():
    CASSETTE_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    openai_api_key: SecretStr = Field(alias="OPENAI_API_KEY")
    langsmith_api_key: SecretStr = Field(alias="LANGSMITH_API_KEY")
    langsmith_project: str
    langsmith_endpoint: str
    langsmith_tracing: bool

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        populate_by_name=True,
    )


# Don't worry about a type error here, it should load the variable from the .env file
SETTINGS = Settings()  # type: ignore


logger.debug(f"Project root: {PROJECT_ROOT}")
