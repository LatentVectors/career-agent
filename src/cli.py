from __future__ import annotations

import os
import tempfile

import typer
from langchain_core.runnables.config import RunnableConfig

from .db.cli_crud import db_app
from .db.cli_io import dump_app, load_app
from .features.resume import resume_app
from .graph import GRAPH
from .state import get_main_input_state

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

        # Get all companies with job postings
        companies = db_manager.companies.get_all()
        if not companies:
            print("No companies found")
            return

        # Show available companies
        print("Available companies:")
        for i, company in enumerate(companies, 1):
            print(f"{i}. {company.name}")

        # Let user select company
        company_choice = Prompt.ask(
            "Select a company", choices=[str(i) for i in range(1, len(companies) + 1)]
        )
        selected_company = companies[int(company_choice) - 1]

        # Get job postings for the selected company
        jobs = db_manager.job_postings.get_by_company_id(selected_company.id)
        if not jobs:
            print(f"No job postings found for {selected_company.name}")
            return

        # If multiple jobs, let user select one
        if len(jobs) > 1:
            print(f"Available jobs for {selected_company.name}:")
            for i, job in enumerate(jobs, 1):
                print(f"{i}. Job posting {job.id}")
            job_choice = Prompt.ask(
                "Select a job", choices=[str(i) for i in range(1, len(jobs) + 1)]
            )
            selected_job = jobs[int(job_choice) - 1]
        else:
            selected_job = jobs[0]

        print(f"Job: {selected_company.name}")

        # Get user data for the session
        # TODO: This need to be passed to the input state.
        user_education = db_manager.educations.get_by_user_id(user_id)
        user_certifications = db_manager.certifications.get_by_user_id(user_id)
        user_experience = db_manager.experiences.get_by_user_id(user_id)
        user_responses = db_manager.candidate_responses.get_by_user_id(user_id)

        # TODO: Read motivations and interests should just be candidate responses from the database..
        # TODO: Interview questions will be removed later.
        # TODO: Read experience should just be experience from the database..
        input_state = get_main_input_state(
            selected_job, motivations_and_interests=None, interview_questions=None, experience=None
        )
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
