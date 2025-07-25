from typing import List, TypedDict

from langsmith import Client
from langsmith.schemas import ExampleCreate
from src.config import DATA_DIR
from src.logging_config import logger
from src.storage.FileStorage import FileStorage

from evals.datasets.utils import add_examples, verify_dataset

JOBS_DATASET_NAME = "Jobs"


class JobsInput(TypedDict):
    """The input to the job description parsing experiment."""

    job_description: str
    """The job description."""


class JobsRequirementsOutput(TypedDict):
    """The output of the job description parsing experiment."""

    requirements: List[str]
    """The requirements for the job."""


class JobsMetadata(TypedDict):
    """The metadata for the jobs dataset."""

    job_name: str
    """The name of the job."""


def jobs(reset: bool = False) -> None:
    """Create or update the jobs dataset.

    Args:
        reset: Whether to reset the dataset.
    """
    dataset_name = JOBS_DATASET_NAME
    description = "Job descriptions."
    client = Client()
    dataset_id = verify_dataset(client, dataset_name, description, reset)
    examples: List[ExampleCreate] = []
    storage = FileStorage(DATA_DIR)
    for job_name in storage.list_jobs():
        job = storage.get_job(job_name)
        inputs: JobsInput = {
            "job_description": job.description,
        }
        outputs: JobsRequirementsOutput = {
            "requirements": job.parsed_requirements or [],
        }
        metadata: JobsMetadata = {"job_name": job_name}
        logger.debug(f"Adding: {metadata}")
        examples.append(ExampleCreate(inputs=inputs, outputs=outputs, metadata=metadata))
    add_examples(client, dataset_id, examples)
