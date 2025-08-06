from __future__ import annotations

import typer

app = typer.Typer(help="Resume management commands")


@app.command()
def generate() -> None:
    """Generate PDF samples for all resume templates using dummy data."""
    from pathlib import Path

    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table

    from src.config import DATA_DIR

    from .content import DUMMY_RESUME_DATA
    from .utils import get_pdf_info, list_available_templates, render_template_to_pdf

    console = Console()

    # Define templates directory and output directory
    templates_dir = Path("src/features/resume/templates")
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
            # Update progress description to show current template
            progress.update(task, description=f"Processing {template_name}...")

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
