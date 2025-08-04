from __future__ import annotations

import os
import tempfile

import typer
from langchain_core.runnables.config import RunnableConfig

from src.storage import get_background

from .graph import GRAPH
from .state import get_main_input_state

app = typer.Typer()


@app.command()
def save_job(company_name: str) -> None:
    """Save a job to the file storage."""
    from .config import DATA_DIR
    from .storage.FileStorage import FileStorage
    from .storage.parse_job import Job

    job = Job(
        company_name=company_name.strip(),
        description="",
    )

    storage = FileStorage(DATA_DIR)
    if storage.job_exists(company_name):
        typer.echo(f"Job {company_name} already exists")
        replace = typer.confirm("Replace job?")
        if not replace:
            return
    storage.save_job(job)
    typer.echo(f"Job {company_name} saved")


@app.command()
def graph(
    png: bool = typer.Option(False, "--png", help="Draw the graph as a PNG."),
) -> None:
    """Draw the graph."""

    print("=" * 75)
    print("MAIN GRAPH\n")
    print(GRAPH.get_graph().draw_ascii())
    print("\n" * 2)

    if not png:
        return

    from PIL import Image

    img = GRAPH.get_graph().draw_mermaid_png()

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        temp_file.write(img)
        temp_file_path = temp_file.name

    try:
        image = Image.open(temp_file_path)
        image.show()
        typer.echo("Graph displayed in popup window")
    except Exception as e:
        typer.echo(f"Error displaying graph: {e}")
    finally:
        try:
            os.unlink(temp_file_path)
        except OSError:
            pass


@app.command()
def chat(
    replay: bool = typer.Option(False, "--replay", help="Replay recorded requests."),
    thread_id: str = typer.Option("1", "--thread-id", help="A thread ID for the agent config."),
) -> None:
    """Chat with the agent."""
    from rich.prompt import Prompt
    from vcr import VCR  # type: ignore

    from .callbacks import LoggingCallbackHandler
    from .config import CASSETTE_DIR, DATA_DIR
    from .graph import stream_agent
    from .logging_config import logger
    from .storage.FileStorage import FileStorage
    from .utils import serialize_state

    vcr = VCR(
        cassette_library_dir=str(CASSETTE_DIR),
        match_on=("method", "uri", "body", "query"),
        record_mode="new_episodes" if replay else "all",
    )

    try:
        storage = FileStorage(DATA_DIR)
        jobs = storage.list_jobs()
        if not jobs:
            print("No jobs found")
            return
        job_name = Prompt.ask("Select a job", choices=[j.strip(".md") for j in jobs])
        job = storage.get_job(job_name)
        background = get_background(storage)

        print(f"Job: {job_name}")
        print("Background:")
        for experience in background["experience"]:
            print(f"\t\t{experience.title}")
        print()
        print(f"\tMotivations and Interests ({len(background['motivations_and_interests'])})")
        print(f"\tInterview Questions ({len(background['interview_questions'])})")
        print()

        input_state = get_main_input_state(job, background)
        config: RunnableConfig = {
            "configurable": {"thread_id": thread_id},
            "callbacks": [LoggingCallbackHandler()],
        }

        # Wrap the execution in a VCR cassette to capture all requests.
        with vcr.use_cassette("chat.yaml"):
            graph = stream_agent(input_state, config)

        final_state = graph.get_state(config=config)
        output_path = DATA_DIR / "state.json"
        with open(output_path, "w") as f:
            f.write(serialize_state(final_state.values))

        cover_letter = final_state.values.get("cover_letter")
        if cover_letter:
            print("\n\n=== COVER LETTER ===\n")
            print(cover_letter, end="\n\n")
    except Exception as e:
        logger.exception(f"Error chatting: {e}")
        raise e


if __name__ == "__main__":
    app()
