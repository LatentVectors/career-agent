from __future__ import annotations

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
def graph() -> None:
    """Draw the graph."""
    from .agents.experience.graph import experience_graph

    print("=" * 75)
    print("MAIN GRAPH\n")
    print(GRAPH.get_graph().draw_ascii())
    print("\n" * 2)

    print("=" * 75)
    print("EXPERIENCE GRAPH\n")
    print(experience_graph.get_graph().draw_ascii())
    print("\n" * 2)
    print("=" * 75)


@app.command()
def chat() -> None:
    """Chat with the agent."""
    from rich.prompt import Prompt

    from .callbacks import LoggingCallbackHandler
    from .config import DATA_DIR
    from .logging_config import logger
    from .storage.FileStorage import FileStorage

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
            "configurable": {"thread_id": "1"},
            "callbacks": [LoggingCallbackHandler()],
        }

        for event in GRAPH.stream(input_state, config=config):  # type: ignore[arg-type]
            print(event)
        print("=" * 75)
        final_state = GRAPH.get_state(config=config)
        experience_summary = final_state.values.get("experience_summary")
        if experience_summary is None:
            print("No experience summary")
        else:
            print(experience_summary)
    except Exception as e:
        logger.error(f"Error chatting: {e}", exc_info=True)
        raise e


if __name__ == "__main__":
    app()
