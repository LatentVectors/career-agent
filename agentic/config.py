import sys
from pathlib import Path

from langchain_chroma.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from loguru import logger
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

logger.remove()
logger.add(sys.stdout, format="{message}", colorize=True, level="INFO")
logger.add("logs/agentic.log", level="DEBUG", rotation="10 MB")

PROJECT_ROOT = Path(__file__).parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

CHROMA_DB_DIR = PROCESSED_DATA_DIR / ".chroma"

if not DATA_DIR.exists():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

if not RAW_DATA_DIR.exists():
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

if not INTERIM_DATA_DIR.exists():
    INTERIM_DATA_DIR.mkdir(parents=True, exist_ok=True)

if not PROCESSED_DATA_DIR.exists():
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)


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


def get_vector_store() -> Chroma:
    """Get a vector store for the Paul Graham articles."""
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_store = Chroma(
        collection_name="paul_graham_articles",
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DB_DIR),
    )
    return vector_store


logger.debug(f"Project root: {PROJECT_ROOT}")
