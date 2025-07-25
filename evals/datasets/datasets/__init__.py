from typing import Callable, Dict

from .jobs import JOBS_DATASET_NAME, JobsInput, JobsMetadata, jobs
from .jobs_and_experience import (
    JOBS_AND_EXPERIENCE_DATASET_NAME,
    JobsAndExperienceInput,
    JobsAndExperienceMetadata,
    jobs_and_experience,
)

DATASETS: Dict[str, Callable[[bool], None]] = {
    JOBS_DATASET_NAME: jobs,
    JOBS_AND_EXPERIENCE_DATASET_NAME: jobs_and_experience,
}

__all__ = [
    "DATASETS",
    "JOBS_DATASET_NAME",
    "JOBS_AND_EXPERIENCE_DATASET_NAME",
    "JobsInput",
    "JobsMetadata",
    "JobsAndExperienceInput",
    "JobsAndExperienceMetadata",
]
