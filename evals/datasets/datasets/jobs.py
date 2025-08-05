"""Dataset builder for job descriptions using database backend."""

from __future__ import annotations

import json
from typing import List, TypedDict

from langsmith import Client
from langsmith.schemas import ExampleCreate
from src.db.database import db_manager
from src.logging_config import logger

from evals.datasets.utils import add_examples, verify_dataset

JOBS_DATASET_NAME = "Jobs"


class JobsInput(TypedDict):
    """Input schema for job description dataset."""

    job_description: str


class JobsRequirementsOutput(TypedDict):
    """Output schema for parsed job requirements."""

    requirements: List[str]


class JobsMetadata(TypedDict):
    """Metadata schema for jobs dataset."""

    job_id: str


def jobs(reset: bool = False) -> None:
    """Create or update the jobs dataset from the database.

    Args:
        reset: Whether to reset (delete & recreate) the dataset on LangSmith.
    """
    dataset_name = JOBS_DATASET_NAME
    description = "Job descriptions."
    client = Client()
    dataset_id = verify_dataset(client, dataset_name, description, reset)

    examples: List[ExampleCreate] = []

    for job in db_manager.job_postings.get_all():
        inputs: JobsInput = {"job_description": job.description}

        # Parse requirements JSON string into list if available, else []
        try:
            requirements_parsed = json.loads(job.requirements) if job.requirements else []
        except json.JSONDecodeError:
            requirements_parsed = []

        outputs: JobsRequirementsOutput = {"requirements": requirements_parsed}
        metadata: JobsMetadata = {"job_id": str(job.id)}
        logger.debug(f"Adding: {metadata}")
        examples.append(ExampleCreate(inputs=inputs, outputs=outputs, metadata=metadata))

    add_examples(client, dataset_id, examples)
