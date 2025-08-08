"""Generate experience bullets node for resume generation."""

from __future__ import annotations

from langgraph.runtime import Runtime

from src.context import AgentContext
from src.logging_config import logger

from ..state import InternalState, PartialInternalState


def generate_experience_bullets(
    state: InternalState, runtime: Runtime[AgentContext]
) -> PartialInternalState:
    """Generate tailored bullet points for each experience.

    Args:
        state: Current state containing experience_data and job_title

    Returns:
        Updated state with generated experience bullets
    """
    logger.debug("NODE: resume_generator.generate_experience_bullets")
    experience_data = state.experience_data or []
    job_title = state.job_title
    job_description = state.job_description

    logger.debug(f"Generating experience bullets for {len(experience_data)} experiences")

    if not experience_data:
        logger.warning("No experience data available for bullet generation")
        return {"resume_data": None}

    # Process each experience to generate bullets
    processed_experiences = []

    for experience in experience_data:
        try:
            bullets = _generate_bullets_for_experience(experience, job_title, job_description)
            processed_experiences.append(
                {
                    "id": experience.id,
                    "title": experience.title,
                    "company": experience.company,
                    "location": experience.location,
                    "start_date": experience.start_date,
                    "end_date": experience.end_date,
                    "points": bullets,
                }
            )
            logger.info(f"Generated {len(bullets)} bullets for experience at {experience.company}")

        except Exception as e:
            logger.exception(f"Error generating bullets for experience {experience.id}: {e}")
            # Add experience with empty bullets on error
            processed_experiences.append(
                {
                    "id": experience.id,
                    "title": experience.title,
                    "company": experience.company,
                    "location": experience.location,
                    "start_date": experience.start_date,
                    "end_date": experience.end_date,
                    "points": [],
                }
            )

    return {
        "resume_data": {"experience": processed_experiences},
        "processed_experiences": [exp["id"] for exp in processed_experiences],
    }
