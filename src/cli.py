from __future__ import annotations

import os
import tempfile

import typer
from langchain_core.runnables.config import RunnableConfig

from .context import AgentContext
from .db.cli_crud import db_app
from .db.cli_io import dump_app, load_app
from .features.resume import resume_app
from .graph import GRAPH
from .state import InputState

app = typer.Typer()

# Add database commands
app.add_typer(db_app, name="db")

# Add I/O commands
app.add_typer(dump_app, name="dump")
app.add_typer(load_app, name="load")

# Add resume commands
app.add_typer(resume_app, name="resume")


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
    user_id: int = typer.Option(1, "--user-id", help="The user ID to use for the chat session."),
) -> None:
    """Chat with the agent."""
    from rich.prompt import Prompt
    from vcr import VCR  # type: ignore

    from .callbacks import LoggingCallbackHandler
    from .config import CASSETTE_DIR, DATA_DIR
    from .db import db_manager
    from .graph import stream_agent
    from .logging_config import logger
    from .utils import serialize_state

    vcr = VCR(
        cassette_library_dir=str(CASSETTE_DIR),
        match_on=("method", "uri", "body", "query"),
        record_mode="new_episodes" if replay else "all",
    )

    try:
        # Get user
        user = db_manager.users.get_by_id(user_id)
        if user is None:
            typer.echo(f"No user found with ID {user_id}.")
            raise typer.Exit(code=1)

        # Get all job postings
        job_postings = db_manager.job_postings.get_all()
        if not job_postings:
            print("No job postings found")
            return

        # Show available job postings
        print("Available job postings:")
        for i, job in enumerate(job_postings, 1):
            company_name = "Unknown Company"
            if job.company_id:
                company = db_manager.companies.get_by_id(job.company_id)
                if company:
                    company_name = company.name
            print(f"{i}. {job.title} at {company_name}")

        # Let user select job posting
        job_choice = Prompt.ask(
            "Select a job posting", choices=[str(i) for i in range(1, len(job_postings) + 1)]
        )
        selected_job = job_postings[int(job_choice) - 1]

        # Get company name for display
        company_name = "Unknown Company"
        if selected_job.company_id:
            company = db_manager.companies.get_by_id(selected_job.company_id)
            if company:
                company_name = company.name

        print(f"Selected: {selected_job.title} at {company_name}")

        # Build runtime context for the graph execution
        ctx = AgentContext(user_id=user_id, job_posting_id=selected_job.id)

        # Build the minimal input state required for the graph execution
        input_state = InputState(
            job_description=selected_job.description,
            experience_ids=[exp.id for exp in db_manager.experiences.get_by_user_id(user_id)],
        )
        config: RunnableConfig = {
            "configurable": {"thread_id": thread_id},
            "callbacks": [LoggingCallbackHandler()],
        }

        # Wrap the execution in a VCR cassette to capture all requests.
        with vcr.use_cassette("chat.yaml"):
            graph = stream_agent(input_state, config, context=ctx)

        final_state = graph.get_state(config=config)
        output_path = DATA_DIR / "state.json"
        with open(output_path, "w") as f:
            f.write(serialize_state(final_state.values))

        cover_letter = final_state.values.get("cover_letter")
        resume = final_state.values.get("resume")
        if cover_letter:
            print("\n\n=== COVER LETTER ===\n")
            print(cover_letter)
        if resume:
            print("\n\n=== RESUME ===\n")
            print(resume)
    except Exception as e:
        logger.exception(f"Error chatting: {e}")
        raise e


if __name__ == "__main__":
    app()
