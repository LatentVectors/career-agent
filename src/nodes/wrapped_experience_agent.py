from langgraph.runtime import Runtime

from src.context import AgentContext
from src.logging_config import logger

from ..agents.experience_summarizer import (
    InputState,
    OutputState,
    experience_agent,
)
from ..state import InternalState, PartialInternalState, Summary


def wrapped_experience_agent(
    state: InternalState,
    runtime: Runtime[AgentContext],
) -> PartialInternalState:
    """Delegate summarization of a single experience to the experience_summarizer sub-agent.

    This wrapper remains DB-free and simply forwards the current experience_id and job
    requirements to the dedicated summarizer graph, making sure to preserve the
    execution context so the sub-agent can look up the full Experience record on-demand.
    """
    logger.debug("NODE: wrapped_experience_agent")

    exp_id = state.current_experience_id
    if exp_id is None:
        raise ValueError(
            "current_experience_id must be set before calling wrapped_experience_agent"
        )

    job_requirements = state.job_requirements
    if job_requirements is None:
        raise ValueError("Job requirements are required")

    # Invoke the sub-graph with the same runtime context so it can fetch data as needed.
    result = experience_agent.invoke(
        InputState(
            experience_id=exp_id,
            job_requirements=job_requirements,
        ),
        context=runtime.context,
    )

    validated = OutputState.model_validate(result)
    logger.debug(f"Experience summarizer result: {validated}")

    summaries = validated.summary
    key = f"experience_{exp_id}"
    if len(summaries) == 0:
        logger.debug("No summaries found. Returning empty summary.")
        return PartialInternalState(summarized_experience={key: []})

    return PartialInternalState(
        summarized_experience={
            key: [
                Summary(
                    requirements=summary.requirement,
                    summary=summary.summary,
                )
                for summary in summaries
            ]
        }
    )
