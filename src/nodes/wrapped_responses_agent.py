from src.storage.parse_motivations_and_interests import MotivationAndInterest
from src.types import CandidateResponse

from ..agents.responses_summarizer import (
    ResponsesInputState,
    ResponsesOutputState,
    responses_agent,
)
from ..logging_config import logger
from ..state import MainState, PartialMainState


def wrapped_responses_agent(state: MainState) -> PartialMainState:
    """Wrapped responses agent."""
    logger.info("NODE: wrapped_responses_agent")
    motivations_and_interests = state["motivations_and_interests"]
    if not motivations_and_interests:
        return {"summarized_responses": {}}

    job_requirements = state["job_requirements"]
    if not job_requirements:
        raise ValueError("Job requirements are required")
    input_state: ResponsesInputState = {
        "responses": to_candidate_response(motivations_and_interests),
        "job_requirements": job_requirements,
        "source": "responses",
    }
    result: ResponsesOutputState = responses_agent.invoke(input_state)  # type: ignore
    return {
        "summarized_responses": {
            "motivations_and_interests": [
                {
                    "requirements": summary.requirements,
                    "summary": summary.summary,
                }
                for summary in result["summaries"]
            ]
        }
    }


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
