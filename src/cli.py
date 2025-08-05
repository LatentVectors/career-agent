from __future__ import annotations

import os
import tempfile

import typer
from langchain_core.runnables.config import RunnableConfig

from src.storage import get_background

from .graph import GRAPH
from .state import get_main_input_state

app = typer.Typer()

# ---------------------------------------------------------------------------
# User profile commands
# ---------------------------------------------------------------------------
user_app = typer.Typer(help="Manage user profile data.")
app.add_typer(user_app, name="user")


# NOTE: We import inside commands to avoid heavy dependencies at CLI startup.
@user_app.command("show")
def user_show() -> None:  # noqa: D401
    """Display the stored user profile."""

    from rich.pretty import pprint  # Lazy import

    from .config import DATA_DIR
    from .storage.FileStorage import FileStorage

    storage = FileStorage(DATA_DIR)
    profile = storage.get_user_profile()

    if profile.is_empty:
        typer.echo("No user profile found. Use 'agentic user set' to create one.")
        return

    pprint(profile.model_dump())


@user_app.command("set")
def user_set(
    field: str = typer.Argument(..., help="Field to update: name, email, phone, linkedin_url"),
    value: str = typer.Argument(..., help="New value for the field."),
) -> None:  # noqa: D401
    """Set or update a scalar field of the profile."""

    from .config import DATA_DIR
    from .storage.FileStorage import FileStorage

    allowed = {"name", "email", "phone", "linkedin_url"}
    if field not in allowed:
        typer.echo(f"Unknown field '{field}'. Allowed fields: {', '.join(sorted(allowed))}.")
        raise typer.Exit(code=1)

    storage = FileStorage(DATA_DIR)
    profile = storage.get_user_profile()
    setattr(profile, field, value)
    storage.save_user_profile(profile)
    typer.echo(f"Updated {field}.")


@user_app.command("add-education")
def user_add_education(
    degree: str = typer.Option(..., prompt=True),
    major: str = typer.Option(..., prompt=True),
    institution: str = typer.Option(..., prompt=True),
    grad_date: str = typer.Option(..., prompt=True, help="Graduation date, e.g. 2024-05"),
) -> None:  # noqa: D401
    """Append an education entry to the profile."""

    from .config import DATA_DIR
    from .resume.types import Education
    from .storage.FileStorage import FileStorage

    storage = FileStorage(DATA_DIR)
    profile = storage.get_user_profile()

    profile.education.append(
        Education(
            degree=degree,
            major=major,
            institution=institution,
            grad_date=grad_date,
        )
    )
    storage.save_user_profile(profile)
    typer.echo("Education added.")


@user_app.command("add-cert")
def user_add_certification(
    title: str = typer.Option(..., prompt=True),
    date: str = typer.Option(..., prompt=True, help="Date obtained, e.g. 2023-11"),
) -> None:  # noqa: D401
    """Append a certification entry to the profile."""

    from .config import DATA_DIR
    from .resume.types import Certification
    from .storage.FileStorage import FileStorage

    storage = FileStorage(DATA_DIR)
    profile = storage.get_user_profile()

    profile.certifications.append(Certification(title=title, date=date))
    storage.save_user_profile(profile)
    typer.echo("Certification added.")


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


@app.command()
def resume_samples() -> None:
    """Generate PDF samples for all resume templates using dummy data."""
    from pathlib import Path

    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table

    from .config import DATA_DIR
    from .resume.content import DUMMY_RESUME_DATA
    from .resume.utils import get_pdf_info, list_available_templates, render_template_to_pdf

    console = Console()

    # Define templates directory and output directory
    templates_dir = Path("src/resume/templates")
    samples_dir = DATA_DIR / "samples" / "resumes"
    samples_dir.mkdir(parents=True, exist_ok=True)

    # Get available templates
    try:
        templates = list_available_templates(templates_dir)
        console.print(f"[green]Found {len(templates)} templates[/green]")
    except Exception as e:
        console.print(f"[red]Error listing templates: {e}[/red]")
        return

    # Create a table to display results
    table = Table(title="Resume Sample Generation Results")
    table.add_column("Template", style="cyan")
    table.add_column("Profile", style="magenta")
    table.add_column("Pages", style="green")
    table.add_column("Size (MB)", style="yellow")
    table.add_column("Status", style="bold")

    # Generate samples for each template with different profiles
    profile_names = list(DUMMY_RESUME_DATA.keys())

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating resume samples...", total=len(templates))

        for i, template_name in enumerate(templates):
            # Use different profile for each template (cycling through profiles)
            profile_name = profile_names[i % len(profile_names)]
            profile_data = DUMMY_RESUME_DATA[profile_name]

            # Convert ResumeData to dict for template rendering
            context = {
                "name": profile_data.name,
                "title": profile_data.title,
                "email": profile_data.email,
                "phone": profile_data.phone,
                "linkedin_url": profile_data.linkedin_url,
                "professional_summary": profile_data.professional_summary,
                "experience": [
                    {
                        "title": exp.title,
                        "company": exp.company,
                        "location": exp.location,
                        "start_date": exp.start_date,
                        "end_date": exp.end_date,
                        "points": exp.points,
                    }
                    for exp in profile_data.experience
                ],
                "skills": profile_data.skills,
                "education": [
                    {
                        "degree": edu.degree,
                        "major": edu.major,
                        "institution": edu.institution,
                        "grad_date": edu.grad_date,
                    }
                    for edu in profile_data.education
                ],
                "certifications": [
                    {
                        "title": cert.title,
                        "date": cert.date,
                    }
                    for cert in profile_data.certifications
                ],
            }

            # Generate filename
            template_base = template_name.replace(".html", "")
            output_filename = f"{template_base}_{profile_name}.pdf"
            output_path = samples_dir / output_filename

            try:
                # Generate PDF
                pdf_path = render_template_to_pdf(
                    template_name, context, output_path, templates_dir
                )

                # Get PDF info
                info = get_pdf_info(pdf_path)

                # Add to table
                table.add_row(
                    template_name,
                    profile_name.replace("_", " ").title(),
                    str(info["page_count"]),
                    f"{info['file_size_mb']:.2f}",
                    "✅ Generated",
                )

            except Exception as e:
                table.add_row(
                    template_name,
                    profile_name.replace("_", " ").title(),
                    "-",
                    "-",
                    f"❌ Error: {str(e)[:50]}...",
                )

            progress.advance(task)

    # Display results
    console.print("\n")
    console.print(table)
    console.print(f"\n[green]Samples saved to: {samples_dir}[/green]")

    # List generated files
    generated_files = list(samples_dir.glob("*.pdf"))
    if generated_files:
        console.print(f"\n[blue]Generated {len(generated_files)} sample files:[/blue]")
        for file in sorted(generated_files):
            console.print(f"  • {file.name}")


if __name__ == "__main__":
    app()
