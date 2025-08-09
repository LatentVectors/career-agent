from __future__ import annotations

import importlib
import os
import pkgutil
import tempfile
from typing import Any

import typer
from langchain_core.runnables.config import RunnableConfig

from .agents.main.graph import GRAPH
from .agents.main.state import InputState
from .core.context import AgentContext
from .db.cli_crud import db_app
from .db.cli_io import dump_app, load_app
from .features.resume import resume_app

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
    agent: str | None = typer.Option(
        None,
        "--agent",
        "-a",
        help=(
            "Agent graph to display. If omitted, you will be prompted to choose. "
            "Options include 'main' and discovered sub-agents."
        ),
    ),
) -> None:
    """Draw the selected graph (main or a discovered sub-agent)."""

    # Discover sub-agent graphs before prompting
    sub_agents = _discover_agent_graphs()
    options: list[str] = sorted(sub_agents.keys())

    # Resolve selection
    selected_key: str
    if agent is None:
        # Prompt user to choose an agent graph to display
        try:
            from rich.prompt import Prompt  # Local import to keep CLI startup lean
        except Exception:
            Prompt = None  # type: ignore

        print("Available agents:")
        for i, name in enumerate(options, start=1):
            print(f"{i}. {name}")

        if Prompt is not None:
            choice = Prompt.ask(
                "Select an agent graph to display",
                choices=[str(i) for i in range(1, len(options) + 1)],
            )
            selected_key = options[int(choice) - 1]
        else:
            # Fallback: default to 'main' if rich is unavailable
            selected_key = "main"
    else:
        normalized = agent.strip().lower()
        if normalized not in [opt.lower() for opt in options]:
            typer.echo(
                f"Unknown agent '{agent}'. Valid options: {', '.join(options)}",
            )
            raise typer.Exit(code=1)
        # Map back to canonical option name
        for opt in options:
            if opt.lower() == normalized:
                selected_key = opt
                break

    # Select the graph object
    selected_graph = GRAPH if selected_key == "main" else sub_agents[selected_key]

    print("=" * 75)
    print(f"SELECTED GRAPH: {selected_key}\n")
    try:
        print(selected_graph.get_graph().draw_ascii())
    except Exception:
        typer.echo("Unable to render ASCII graph for the selected agent.")
    print("\n" * 2)

    if not png:
        return

    def _show_png_for(graph_obj: Any) -> None:
        from PIL import Image  # Lazy import

        img_bytes = graph_obj.get_graph().draw_mermaid_png()
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            temp_file.write(img_bytes)
            temp_file_path = temp_file.name

        try:
            image = Image.open(temp_file_path)
            image.show()
            typer.echo("Graph displayed in popup window")
        except Exception as e:  # noqa: BLE001
            typer.echo(f"Error displaying graph: {e}")
        finally:
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass

    # Show PNG for the selected graph only
    _show_png_for(selected_graph)


def _discover_agent_graphs() -> dict[str, Any]:
    """Discover sub-agent compiled graphs dynamically.

    Returns:
        dict[str, Any]: Mapping of agent key (package name) to its compiled graph object.
    """
    try:
        import src.agents as agents_pkg  # type: ignore
    except Exception:
        return {}

    discovered: dict[str, Any] = {}
    for module_info in pkgutil.iter_modules(agents_pkg.__path__):  # type: ignore[attr-defined]
        pkg_name = module_info.name
        try:
            mod = importlib.import_module(f"src.agents.{pkg_name}")
        except Exception:
            continue

        candidate: Any | None = None

        # Preferred convention: attributes ending with "_agent"
        for attr_name in dir(mod):
            if not attr_name.endswith("_agent"):
                continue
            obj = getattr(mod, attr_name)
            # Duck-type check for compiled graph objects
            if hasattr(obj, "get_graph") and callable(getattr(obj, "get_graph", None)):
                candidate = obj
                break

        # Fallback to common name "graph"
        if candidate is None and hasattr(mod, "graph"):
            obj = getattr(mod, "graph")
            if hasattr(obj, "get_graph") and callable(getattr(obj, "get_graph", None)):
                candidate = obj

        if candidate is not None:
            discovered[pkg_name] = candidate

    return discovered


@app.command()
def chat(
    replay: bool = typer.Option(False, "--replay", help="Replay recorded requests."),
    thread_id: str = typer.Option("1", "--thread-id", help="A thread ID for the agent config."),
    user_id: int = typer.Option(1, "--user-id", help="The user ID to use for the chat session."),
) -> None:
    """Chat with the agent."""
    from rich.prompt import Prompt
    from vcr import VCR  # type: ignore

    from .agents.main.graph import stream_agent
    from .config import CASSETTE_DIR, DATA_DIR
    from .core.callbacks import LoggingCallbackHandler
    from .db import db_manager
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
