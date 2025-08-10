from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from src.core.models import OpenAIModels, get_model
from src.logging_config import logger

from ..state import InternalState, PartialInternalState


def summarize_experience(state: InternalState) -> PartialInternalState:
    """Summarize a single experience for resume content generation.

    Overview:
        For the experience indicated by `state.current_experience_id`, produce a concise,
        grounded summary (3–5 sentences) that highlights measurable impact and alignment to
        the provided job description. This summary is later used to help compose the
        professional summary.

    Preconditions:
        - `state.current_experience_id` must be set
        - `state.job_description` must be non-empty
        - The referenced experience must exist and include non-empty `content`

    Reads:
        - job_description
        - current_experience_id
        - experience[current_experience_id]

    Returns:
        - experience_summary: dict[int, str]
          Reduced by dict-merge with the experience id as the key.
    """
    logger.debug("NODE: summarize_experience")

    exp_id = state.current_experience_id
    if exp_id is None:
        logger.warning("current_experience_id is not set; skipping summarization.")
        return PartialInternalState()

    job_description = state.job_description
    if not job_description:
        logger.warning("job_description is empty; skipping summarization.")
        return PartialInternalState()

    experience = state.experience.get(exp_id)
    if experience is None or not getattr(experience, "content", None):
        logger.warning(
            "Experience not found or has no content; skipping summarization. exp_id=%s", exp_id
        )
        return PartialInternalState()

    # Prepare inputs for the model
    experience_text = _format_experience_content(
        title=experience.title,
        company=experience.company,
        location=experience.location,
        content=experience.content,
    )

    try:
        result = _chain.invoke(
            {
                "job_description": job_description,
                "experience": experience_text,
            }
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to summarize experience: %s", exc)
        return PartialInternalState()

    validated = NodeOutput.model_validate(result)
    summary = validated.summary.strip()
    if not summary:
        return PartialInternalState()
    return PartialInternalState(experience_summary={exp_id: summary})


def _format_experience_content(*, title: str, company: str, location: str, content: str) -> str:
    """Format an experience's fields into a compact, model-friendly string."""
    header_bits: list[str] = []
    if title:
        header_bits.append(title)
    if company:
        header_bits.append(company)
    if location:
        header_bits.append(location)
    header = " | ".join(bit for bit in header_bits if bit)
    if header:
        return f"{header}\n\n{content}"
    return content


# === Prompts ===
_system_prompt = """
You are an expert resume writer. Given a job description and a single work experience, write a concise, professional summary (3–5 sentences) that:

- Is strictly grounded in the provided experience text (do not invent facts)
- Highlights measurable impact, scope, and technologies where present
- Mirrors relevant language from the job description when appropriate
- Emphasizes how the experience aligns with the target role

Return a JSON object matching the provided schema.
"""

_user_prompt = """
<JobDescription>
{job_description}
</JobDescription>

<Experience>
{experience}
</Experience>
"""


# === Structured output model ===
class NodeOutput(BaseModel):
    """Structured result of the summarization step."""

    summary: str = Field(
        ..., description="A concise 3–5 sentence summary grounded in the experience."
    )


# === Chain ===
_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", _system_prompt),
        ("user", _user_prompt),
    ]
)
_llm = get_model(OpenAIModels.gpt_4o_mini).with_structured_output(NodeOutput)
_chain = _prompt | _llm
