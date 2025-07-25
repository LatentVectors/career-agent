import typer

from evals.experiments.job_requirements import evaluate_job_requirements

app = typer.Typer(help="Execute experiment commands")

app.command("job-requirements")(evaluate_job_requirements)
