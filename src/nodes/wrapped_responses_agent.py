from src.storage.parse_motivations_and_interests import MotivationAndInterest
from src.types import CandidateResponse

from ..agents.responses_summarizer import (
    InputState,
    OutputState,
    responses_agent,
)
from ..logging_config import logger
from ..state import InternalState, PartialInternalState, Summary


def wrapped_responses_agent(state: InternalState) -> PartialInternalState:
    """Wrapped responses agent."""
    logger.debug("NODE: wrapped_responses_agent")
    motivations_and_interests = state.motivations_and_interests
    if not motivations_and_interests:
        logger.debug("No motivations and interests found. Returning empty summary.")
        return PartialInternalState(summarized_responses={})

    job_requirements = state.job_requirements
    if not job_requirements:
        raise ValueError("Job requirements are required")
    result = responses_agent.invoke(
        InputState(
            responses=to_candidate_response(motivations_and_interests),
            job_requirements=job_requirements,
            source="responses",
        )
    )
    validated = OutputState.model_validate(result)
    if len(validated.summaries) == 0:
        logger.debug("No summaries found. Returning empty summary.")
        return PartialInternalState(summarized_responses={})
    return PartialInternalState(
        summarized_responses={
            "motivations_and_interests": [
                Summary(
                    requirements=summary.requirements,
                    summary=summary.summary,
                )
                for summary in validated.summaries
            ]
        }
    )


def to_candidate_response(motivations: list[MotivationAndInterest]) -> list[CandidateResponse]:
    """Format motivations and interests.

    Args:
        motivations: The motivations and interests to format.

    Returns:
        A list of candidate responses.
    """
    return [
        CandidateResponse(
            prompt=response.question,
            response=response.answer,
        )
        for response in motivations
    ]
