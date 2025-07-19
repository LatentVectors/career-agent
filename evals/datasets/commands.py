from typing import Optional

import typer
from langsmith import Client
from rich.prompt import Prompt
from src.logging_config import logger

from evals.datasets.datasets import (
    DATASETS,
    jobs,
    jobs_and_experience,
)

app = typer.Typer(help="Execute dataset commands")


@app.command()
def update(
    all: bool = typer.Option(False, "--all", help="Create or update all datasets."),
    reset: bool = typer.Option(False, "--reset", help="Reset the dataset."),
    selected_dataset: Optional[str] = typer.Option(
        None, "--dataset", help="The name of the dataset to create or update."
    ),
) -> None:
    """Create or update datasets."""
    if selected_dataset is None and not all:
        # Interactive selection when no dataset is specified
        selected_dataset = _interactive_dataset_selection()

    if all:
        jobs_and_experience(reset)
        jobs(reset)
    else:
        if selected_dataset in DATASETS:
            DATASETS[selected_dataset](reset)
        else:
            raise ValueError(f"Unknown dataset: {selected_dataset}")


def _interactive_dataset_selection() -> str:
    """Present interactive selection for available datasets."""
    available_datasets = list(DATASETS.keys())

    logger.info("\n[bold blue]Available datasets:[/bold blue]")
    for i, dataset in enumerate(available_datasets, 1):
        logger.info(f"  {i}. {dataset}")

    while True:
        try:
            choice = Prompt.ask(
                "\n[bold green]Select a dataset to update[/bold green]",
                choices=[str(i) for i in range(1, len(available_datasets) + 1)],
            )
            selected_index = int(choice) - 1
            return available_datasets[selected_index]
        except ValueError:
            logger.error("Invalid selection. Please try again.")


@app.command()
def ls() -> None:
    """List metadata about datasets in LangSmith."""
    client = Client()
    datasets = client.list_datasets()

    logger.info("=== DATASETS ===")
    if not datasets:
        logger.info("No datasets found in LangSmith.")
        return

    for dataset in datasets:
        logger.info(f"{dataset.name}")
        logger.info(f"\tDescription: {dataset.description or 'No description'}")
        logger.info(f"\tCreated:\t{dataset.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        modified_at = (
            dataset.modified_at.strftime("%Y-%m-%d %H:%M:%S") if dataset.modified_at else "N/A"
        )
        logger.info(f"\tModified:\t{modified_at}")
        print()
