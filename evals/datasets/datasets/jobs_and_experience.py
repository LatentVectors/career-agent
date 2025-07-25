from typing import List, TypedDict

from langsmith import Client
from langsmith.schemas import ExampleCreate
from src.config import DATA_DIR
from src.logging_config import logger
from src.storage.FileStorage import FileStorage

from evals.datasets.utils import add_examples, verify_dataset

JOBS_AND_EXPERIENCE_DATASET_NAME = "Jobs & Experience"


class JobsAndExperienceInput(TypedDict):
    """The input to the job description parsing experiment."""

    job_description: str
    """The job description."""

    experience: str
    """The work experience."""


class JobsAndExperienceMetadata(TypedDict):
    """The metadata for the jobs and experience dataset."""

    job_name: str
    """The name of the job."""

    experience_title: str
    """The title of the work experience."""


def jobs_and_experience(reset: bool = False) -> None:
    """Create or update the jobs and experience dataset.

    Args:
        reset: Whether to reset the dataset.
    """
    dataset_name = JOBS_AND_EXPERIENCE_DATASET_NAME
    description = "Job descriptions and work experiences."
    client = Client()
    dataset_id = verify_dataset(client, dataset_name, description, reset)
    examples: List[ExampleCreate] = []
    storage = FileStorage(DATA_DIR)
    for job_name in storage.list_jobs():
        job = storage.get_job(job_name)
        for experience_name in storage.list_experience():
            experience = storage.get_experience(experience_name)
            inputs: JobsAndExperienceInput = {
                "job_description": job.description,
                "experience": experience,
            }
            metadata: JobsAndExperienceMetadata = {
                "job_name": job_name,
                "experience_title": experience_name,
            }
            logger.debug(f"Adding: {metadata}")
            examples.append(ExampleCreate(inputs=inputs, metadata=metadata))
    add_examples(client, dataset_id, examples)
