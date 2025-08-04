from src.logging_config import logger

from ..agents.experience_summarizer import (
    InputState,
    OutputState,
    experience_agent,
)
from ..state import InternalState, PartialInternalState, Summary


def wrapped_experience_agent(state: InternalState) -> PartialInternalState:
    """Summarize experience."""
    logger.debug("NODE: wrapped_experience_agent")
    title = state.current_experience_title
    if title is None:
        raise ValueError("Current experience title is required")
    experience = state.current_experience
    if experience is None or experience.strip() == "":
        raise ValueError("Current experience is required")
    job_requirements = state.job_requirements
    if job_requirements is None:
        raise ValueError("Job requirements are required")
    result = experience_agent.invoke(
        InputState(
            experience=experience,
            job_requirements=job_requirements,
        )
    )
    validated = OutputState.model_validate(result)
    logger.debug(f"Experience summarizer result: {validated}")
    summaries = validated.summary
    if len(summaries) == 0:
        logger.debug("No summaries found. Returning empty summary.")
        return PartialInternalState(summarized_experience={title: []})
    return PartialInternalState(
        summarized_experience={
            title: [
                Summary(
                    requirements=summary.requirement,
                    summary=summary.summary,
                )
                for summary in summaries
            ]
        }
    )
