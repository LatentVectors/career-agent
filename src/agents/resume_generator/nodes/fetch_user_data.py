"""Fetch user data node for resume generation."""

from __future__ import annotations

from langgraph.runtime import Runtime

from src.context import AgentContext
from src.db.database import db_manager
from src.features.resume.data_adapter import (
    detect_missing_optional_data,
    detect_missing_required_data,
    fetch_candidate_responses,
    fetch_experience_data,
)
from src.features.resume.data_adapter import (
    fetch_user_data as fetch_user_data_func,
)
from src.hitl import dispatch_message_interrupt
from src.logging_config import logger

from ..state import InternalState, PartialInternalState


def fetch_user_data(state: InternalState, runtime: Runtime[AgentContext]) -> PartialInternalState:
    """Fetch and validate user data from database.

    Args:
        state: Current state containing user_id and job_title

    Returns:
        Updated state with user data, experience data, and responses data
    """
    logger.debug("NODE: resume_generator.fetch_user_data")
    user_id = state.user_id
    job_title = state.job_title

    logger.debug(f"Fetching user data for user {user_id} for job title: {job_title}")

    try:
        # Fetch user data
        user_data = fetch_user_data_func(user_id, db_manager)
        experience_data = fetch_experience_data(user_id, db_manager)
        responses_data = fetch_candidate_responses(user_id, db_manager)

        # Check for missing required data
        missing_required = detect_missing_required_data(user_data)
        if missing_required:
            logger.warning(f"Missing required data for user {user_id}: {missing_required}")
            # Use HITL to prompt user for missing required data
            for field in missing_required:
                dispatch_message_interrupt(
                    f"Please provide your {field.replace('_', ' ')} for resume generation."
                )

        # Check for missing optional data
        missing_optional = detect_missing_optional_data(user_data, experience_data, responses_data)
        if missing_optional:
            logger.info(f"Missing optional data for user {user_id}: {missing_optional}")
            # Log warnings for missing optional data but don't block
            for field in missing_optional:
                logger.warning(f"Missing optional data: {field}")

        logger.debug(
            f"Successfully fetched data for user {user_id}: "
            f"{len(experience_data)} experiences, {len(responses_data)} responses"
        )

        return {
            "user_data": user_data,
            "experience_data": experience_data,
            "responses_data": responses_data,
        }

    except ValueError as e:
        logger.error(f"Error fetching user data: {e}")
        # Use HITL to handle the error
        dispatch_message_interrupt(
            f"Error fetching user data: {e}. Please verify your user ID and try again."
        )
        raise

    except Exception as e:
        logger.exception(f"Unexpected error fetching user data: {e}")
        dispatch_message_interrupt(
            f"An unexpected error occurred while fetching your data: {e}. Please try again."
        )
        raise
