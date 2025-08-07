from langgraph.runtime import Runtime

from src.context import AgentContext

from ..agents.responses_summarizer import (
    InputState,
    OutputState,
    responses_agent,
)
from ..logging_config import logger
from ..state import InternalState, PartialInternalState, Summary


def wrapped_responses_agent(
    state: InternalState,
    runtime: Runtime[AgentContext],
) -> PartialInternalState:
    """Summarize candidate responses on-demand using the responses_summarizer sub-agent."""
    logger.debug("NODE: wrapped_responses_agent")

    job_requirements = state.job_requirements
    if not job_requirements:
        raise ValueError("Job requirements are required")

    result = responses_agent.invoke(
        InputState(
            job_requirements=job_requirements,
            source="candidate_responses",
        ),
        context=runtime.context,
    )

    validated = OutputState.model_validate(result)
    if len(validated.summaries) == 0:
        logger.debug("No summaries found. Returning empty summary.")
        return PartialInternalState(summarized_responses={})

    return PartialInternalState(
        summarized_responses={
            "candidate_responses": [
                Summary(
                    requirements=summary.requirements,
                    summary=summary.summary,
                )
                for summary in validated.summaries
            ]
        }
    )
