from __future__ import annotations

from typing import Final

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.core.models import OpenAIModels, get_model
from src.logging_config import logger

from ..state import InternalState, PartialInternalState


def provide_resume_feedback(state: InternalState) -> PartialInternalState:
    """Generate iterative feedback to guide resume content selection.

    Overview:
        Uses an LLM to review the current resume draft along with page-length
        metrics and produce actionable feedback that the content-selection node
        can apply to converge toward the target page length and quality.

    Reads:
        - resume
        - resume_page_length
        - resume_page_target
        - word_count

    Returns:
        - resume_feedback: str
        - feedback_loop_iterations: int (increment by 1 via reducer)
    """
    logger.debug("NODE: resume_generator.provide_resume_feedback")

    # Prepare inputs with safe fallbacks
    resume_text = str(state.resume) if state.resume is not None else ""
    page_length = state.resume_page_length
    page_target = state.resume_page_target
    word_count = state.word_count

    inputs = {
        "resume": resume_text,
        "page_target": f"{page_target:.2f}" if page_target is not None else "",
        "current_page_length": f"{page_length:.2f}" if page_length is not None else "",
        "word_count": str(word_count or ""),
    }

    try:
        feedback = _chain.invoke(inputs).strip()
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to generate resume feedback: %s", exc)
        # Even on failure, increment iteration to avoid infinite loops
        return PartialInternalState(feedback_loop_iterations=1)

    if not feedback:
        return PartialInternalState(feedback_loop_iterations=1)

    # Increment by one via reducer-add semantics and return the feedback
    return PartialInternalState(
        resume_feedback=feedback,
        feedback_loop_iterations=1,
    )


# === Prompt ===
_SYSTEM_PROMPT: Final[str] = """
You are an expert resume editor focused on helping a resume meet a page-length target
while maximizing alignment and impact.

Given the current resume draft and metrics, produce concise, actionable guidance that
the system can apply on the next iteration of content selection.

Guidelines
- Do not invent facts; only reference what could reasonably be adjusted (selection, trimming, deduping, rewording).
- If the resume is too long, recommend which areas to compress or omit (e.g., reduce bullets for less relevant roles,
  tighten verbose bullets, trim skills list).
- If too short, suggest where to expand using available accomplishments/skills and how to strengthen the summary.
- Be specific where possible (e.g., target a number of bullets to add/remove, call out redundant themes to dedupe).
- Keep the feedback brief (5–10 bullet points or a compact paragraph), actionable, and professional.
"""

_USER_PROMPT: Final[str] = """
<TargetPages>
{page_target}
</TargetPages>

<CurrentPages>
{current_page_length}
</CurrentPages>

<CurrentWordCount>
{word_count}
</CurrentWordCount>

<Resume>
{resume}
</Resume>

Return only the feedback text. Do not wrap in JSON.
"""

_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", _SYSTEM_PROMPT),
        ("user", _USER_PROMPT),
    ]
)
_LLM = get_model(OpenAIModels.gpt_4o_mini)
_CHAIN = _PROMPT | _LLM | StrOutputParser()

# Stable symbol for invocation
_chain = _CHAIN
