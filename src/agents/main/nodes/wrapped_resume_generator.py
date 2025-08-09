from __future__ import annotations

from langgraph.runtime import Runtime

from src.agents.resume_generator import (
    InputState as ResumeInputState,
)
from src.agents.resume_generator import (
    OutputState as ResumeOutputState,
)
from src.agents.resume_generator import (
    resume_agent,
)
from src.core.context import AgentContext
from src.logging_config import logger

from ..state import InternalState as MainInternalState
from ..state import PartialInternalState as MainPartialInternalState


def wrapped_resume_generator(
    state: MainInternalState,
    runtime: Runtime[AgentContext],
) -> MainPartialInternalState:
    """Adapter node that runs the resume_generator sub-agent.

    It converts the main agent state to the resume sub-agent input, invokes the
    resume sub-agent with the current runtime context, and returns the relevant
    outputs (formatted resume text and PDF path) back into the main agent state.
    """
    logger.debug("NODE: wrapped_resume_generator")

    job_title = state.job_title
    if not job_title:
        raise ValueError("job_title is required before running the resume generator")

    # Build input for resume sub-agent
    resume_input = ResumeInputState(
        user_id=runtime.context.user_id,
        job_title=job_title,
        job_description=state.job_description,
    )

    result = resume_agent.invoke(resume_input, context=runtime.context)

    validated = ResumeOutputState.model_validate(result)

    return MainPartialInternalState(
        resume_text=validated.resume_text,
        resume_pdf_path=validated.resume_pdf_path,
    )
