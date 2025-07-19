from typing import Callable, Dict, List

from langsmith import Client
from langsmith.schemas import ExampleCreate
from src.config import DATA_DIR
from src.logging_config import logger
from src.storage.FileStorage import FileStorage

from evals.datasets.utils import add_examples, verify_dataset

JOBS_AND_EXPERIENCE_DATASET_NAME = "Jobs & Experience"
JOBS_DATASET_NAME = "Jobs"


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
            inputs = {"job_description": job.description, "experience": experience}
            metadata = {"job_name": job_name, "experience_title": experience_name}
            logger.debug(f"Adding: {metadata}")
            examples.append(ExampleCreate(inputs=inputs, metadata=metadata))
    add_examples(client, dataset_id, examples)


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
        inputs = {
            "job_description": job.description,
        }
        metadata = {"job_name": job_name}
        logger.debug(f"Adding: {metadata}")
        examples.append(ExampleCreate(inputs=inputs, metadata=metadata))
    add_examples(client, dataset_id, examples)


DATASETS: Dict[str, Callable[[bool], None]] = {
    JOBS_AND_EXPERIENCE_DATASET_NAME: jobs_and_experience,
    JOBS_DATASET_NAME: jobs,
}
