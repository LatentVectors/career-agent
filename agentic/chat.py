from pathlib import Path

import typer
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.messages.base import BaseMessage
from langchain_text_splitters.character import RecursiveCharacterTextSplitter

from agentic.config import RAW_DATA_DIR, SETTINGS, get_vector_store, logger
from agentic.scrape import PaulGrahamHTMLLoader, scrape_paul_graham
from agentic.utils import print_max_width

app = typer.Typer()


@app.command()
def main() -> None:
    """Prints the current settings and API keys."""
    print("Welcome to Agentic Chat!")
    print("-" * 80, end="\n\n")

    # Debug logging for API keys
    logger.debug(f"OpenAI API Key exists: {bool(SETTINGS.openai_api_key)}")
    logger.debug(f"LangSmith API Key exists: {bool(SETTINGS.langsmith_api_key)}")

    print("Settings:")
    print(f"  LangSmith Tracing: {SETTINGS.langsmith_tracing}")
    print(f"  LangSmith Project: {SETTINGS.langsmith_project}")
    print(f"  LangSmith Endpoint: {SETTINGS.langsmith_endpoint}")
    print(f"  LangSmith API Key: {SETTINGS.langsmith_api_key or 'NOT SET'}")
    print(f"  OpenAI API Key: {SETTINGS.openai_api_key or 'NOT SET'}")
    print("-" * 80, end="\n\n")


@app.command()
def download_articles(download_dir: Path = RAW_DATA_DIR) -> None:
    """Download the articles from the Paul Graham website."""
    print("DOWNLOADING ARTICLES...")
    scrape_paul_graham(download_dir)
    print("DONE!")


@app.command()
def process_documents(documents_dir: Path = RAW_DATA_DIR) -> None:
    """Process documents into the vector store for retrieval.

    Args:
        documents_dir: The directory containing the documents to process.
        db_dir: The directory to save the vector store.
    """
    print("PROCESSING DOCUMENTS...")
    vector_store = get_vector_store()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, add_start_index=True
    )
    pending_files = list(documents_dir.glob("*.html"))
    total_files = len(pending_files)
    for i, file in enumerate(pending_files):
        index = f"{i + 1}/{total_files}"
        matches = vector_store.get(
            where={"filename": file.name}, include=["metadatas", "embeddings"]
        )
        existing_embeddings = matches.get("embeddings")
        existing_ids = matches.get("ids")
        # TODO: Fix this to avoid edge cases.
        # I need to make sure I don't duplicate work while also not missing any segments.
        # If the process fails partway through, I may have missing segments.
        if (
            existing_embeddings is not None
            and existing_ids is not None
            and len(existing_embeddings) == len(existing_ids)
        ):
            print(f"{index} - Skipping {file.stem} because it already exists.")
            continue
        docs = PaulGrahamHTMLLoader(str(file)).load()
        segments = splitter.split_documents(docs)
        ids = [f"{file.stem}::{i}" for i in range(len(segments))]
        print(f"{index} - Adding {len(segments)} segments from {file.stem} to the database...")
        vector_store.add_documents(segments, ids=ids)
    print("DONE!")


@app.command()
def query(query: str) -> None:
    """Query the vector store."""
    vector_store = get_vector_store()
    results = vector_store.similarity_search_with_score(query)
    for result, score in results:
        metadata = result.metadata
        title = metadata.get("title", "N/A")
        date = metadata.get("date", "N/A")
        start_index = metadata.get("start_index")
        content = result.page_content
        print(title)
        print(date, end="\n")
        print(f"- Score: {score}")
        print(f"- Start Index: {start_index}\n")
        print_max_width(content)
        print("-" * 80, end="\n\n")


@app.command()
def chat() -> None:
    model = init_chat_model("gpt-4o-mini", model_provider="openai")
    system_message = SystemMessage(
        "You are a helpful assistant."
        "You are a Doctor Who enthusiast."
        "You are a bit of a nerd."
        "You always try and answer with the most technically correct answer."
        "You have a warm, friendly, and open personality."
        "You are deeply charismatic."
    )

    print("Welcome to Agentic!")
    print("Type 'exit' or 'quit' to end the conversation.")
    print("-" * 80, end="\n\n")
    greeting = AIMessage(content="How may I help you today?")
    print(greeting.content)
    history: list[BaseMessage] = [greeting]
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        history.append(HumanMessage(content=user_input))
        response = "Agent: "
        for token in model.stream(history[:-10] + [system_message]):
            content = str(token.content)
            response += content
            print(content, end="", flush=True)
        print()
        history.append(AIMessage(content=response))


if __name__ == "__main__":
    app()
