from typing import List, Optional
from uuid import UUID

from langsmith import Client
from langsmith.schemas import ExampleCreate
from src.logging_config import logger


def verify_dataset(
    client: Client, dataset_name: str, description: Optional[str] = None, reset: bool = False
) -> UUID:
    """Verify a dataset exists and create it if it doesn't.

    Args:
        client: The LangSmith client.
        dataset_name: The name of the dataset.
        description: The description of the dataset.
        reset: Whether to reset the dataset.

    Returns:
        The dataset id.
    """
    if reset and client.has_dataset(dataset_name=dataset_name):
        logger.info(f"Deleting dataset: {dataset_name}")
        client.delete_dataset(dataset_name=dataset_name)

    dataset_id = None
    if not client.has_dataset(dataset_name=dataset_name):
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description=description,
        )
        dataset_id = dataset.id
        logger.info("Dataset created:")
        logger.info(f"Dataset name: {dataset_name}")
        logger.info(f"Dataset id: {dataset.id}")
    else:
        dataset = client.read_dataset(dataset_name=dataset_name)
        dataset_id = dataset.id
    return dataset_id


def add_examples(client: Client, dataset_id: UUID, examples: List[ExampleCreate]) -> None:
    """Add examples to a dataset.

    Args:
        client: The LangSmith client.
        dataset_id: The id of the dataset.
        examples: The examples to upsert.
    """
    client.create_examples(dataset_id=dataset_id, examples=examples)
    logger.info(f"Successfully created {len(examples)} examples")
