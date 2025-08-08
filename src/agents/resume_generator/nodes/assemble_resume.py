"""Assemble resume node for resume generation."""

from __future__ import annotations

from langgraph.runtime import Runtime

from src.context import AgentContext
from src.features.resume.data_adapter import transform_user_to_resume_data
from src.logging_config import logger

from ..state import InternalState, PartialInternalState


def assemble_resume(state: InternalState, runtime: Runtime[AgentContext]) -> PartialInternalState:
    """Combine all data into ResumeData object.

    Args:
        state: Current state containing all resume components

    Returns:
        Updated state with assembled ResumeData
    """
    logger.debug("NODE: resume_generator.assemble_resume")
    user_data = state.user_data
    experience_data = state.experience_data or []
    responses_data = state.responses_data or []
    job_title = state.job_title

    # Get partial resume data from previous nodes
    partial_resume_data = state.resume_data or {}
    skills = partial_resume_data.get("skills", [])
    experience_bullets = partial_resume_data.get("experience", [])
    professional_summary = partial_resume_data.get("professional_summary", "")

    logger.debug("Assembling complete resume data")

    if not user_data:
        logger.error("No user data available for resume assembly")
        return {"resume_data": None}

    try:
        # Create base ResumeData from user data
        resume_data = transform_user_to_resume_data(
            user_data, experience_data, responses_data, job_title
        )

        # Update with generated content
        if skills:
            resume_data.skills = skills
            logger.debug(f"Added {len(skills)} skills to resume")

        if experience_bullets:
            # Update experience with generated bullets
            for i, exp in enumerate(resume_data.experience):
                if i < len(experience_bullets):
                    exp.points = experience_bullets[i].get("points", [])
            logger.debug(f"Added bullets to {len(experience_bullets)} experiences")

        if professional_summary:
            resume_data.professional_summary = professional_summary
            logger.debug("Added professional summary to resume")

        # Do not update best here; best tracking occurs after PDF generation
        return {"resume_data": resume_data}

    except Exception as e:
        logger.exception(f"Error assembling resume data: {e}")
        return {"resume_data": None}
