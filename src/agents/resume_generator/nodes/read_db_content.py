from __future__ import annotations

from langgraph.runtime import Runtime

from src.core.context import AgentContext
from src.db import db_manager
from src.logging_config import logger

from ..state import InternalState, PartialInternalState


def read_db_content(state: InternalState, runtime: Runtime[AgentContext]) -> PartialInternalState:
    """Load user-scoped records from the DB into working state.

    Reads:
        - context.user_id

    Returns:
        - user: User
        - education: list[Education]
        - credentials: list[Certification]
        - experience: dict[int, Experience]
        - candidate_responses: list[CandidateResponse]
    """
    logger.debug("NODE: resume_generator.read_db_content")

    user_id = runtime.context.user_id
    if user_id is None:  # pragma: no cover - defensive; context schema enforces this
        raise ValueError("context.user_id is required to read DB content")

    user = db_manager.users.get_by_id(user_id)
    if user is None:
        raise ValueError(f"No user found for user_id={user_id}")

    education = db_manager.educations.get_by_user_id(user_id)
    credentials = db_manager.certifications.get_by_user_id(user_id)
    experiences = db_manager.experiences.get_by_user_id(user_id)
    candidate_responses = db_manager.candidate_responses.get_by_user_id(user_id)

    experience_by_id = {exp.id: exp for exp in experiences if getattr(exp, "id", None) is not None}

    return PartialInternalState(
        user=user,
        education=education,
        credentials=credentials,
        experience=experience_by_id,
        candidate_responses=candidate_responses,
    )
