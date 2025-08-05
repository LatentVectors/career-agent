"""Dataset builder combining job descriptions and candidate experiences using DB backend."""

from __future__ import annotations

from typing import List, TypedDict

from langsmith import Client
from langsmith.schemas import ExampleCreate
from src.logging_config import logger
from src.storage.database import db_manager

from evals.datasets.utils import add_examples, verify_dataset

JOBS_AND_EXPERIENCE_DATASET_NAME = "Jobs & Experience"


class JobsAndExperienceInput(TypedDict):
    """Input schema combining job description and experience text."""

    job_description: str
    experience: str


class JobsAndExperienceMetadata(TypedDict):
    """Metadata for each (job, experience) pair."""

    job_id: str
    experience_id: str


def jobs_and_experience(reset: bool = False) -> None:
    """Create or update the jobs & experience dataset from the database.

    Args:
        reset: Whether to reset the dataset on LangSmith.
    """
    dataset_name = JOBS_AND_EXPERIENCE_DATASET_NAME
    description = "Job descriptions and work experiences."
    client = Client()
    dataset_id = verify_dataset(client, dataset_name, description, reset)

    examples: List[ExampleCreate] = []

    jobs = db_manager.job_postings.get_all()
    experiences = db_manager.experiences.get_all()

    for job in jobs:
        for exp in experiences:
            inputs: JobsAndExperienceInput = {
                "job_description": job.description,
                "experience": exp.content,
            }
            metadata: JobsAndExperienceMetadata = {
                "job_id": str(job.id),
                "experience_id": str(exp.id),
            }
            logger.debug(f"Adding: {metadata}")
            examples.append(ExampleCreate(inputs=inputs, metadata=metadata))

    add_examples(client, dataset_id, examples)
