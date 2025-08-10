from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from src.core.models import OpenAIModels, get_model
from src.logging_config import logger

from ..state import InternalState, PartialInternalState, SkillsAndAccomplishments


def extract_skills_and_accomplishments(state: InternalState) -> PartialInternalState:
    """Extract grounded accomplishments and skills for one experience.

    Overview:
        For the experience indicated by `state.current_experience_id`, extract:
        - accomplishments: stand-alone resume-ready bullet points grounded in the experience
        - skills: a deduplicated list of skills present in the experience that align with the job description

    Preconditions:
        - `state.current_experience_id` must be set
        - `state.job_description` must be non-empty
        - The referenced experience must exist and include non-empty `content`

    Reads:
        - job_description
        - current_experience_id
        - experience[current_experience_id]

    Returns:
        - skills_and_accomplishments: dict[int, SkillsAndAccomplishments]
          Reduced by dict-merge with the experience id as the key.
    """
    logger.debug("NODE: extract_skills_and_accomplishments")

    exp_id = state.current_experience_id
    if exp_id is None:
        logger.warning("current_experience_id is not set; skipping extraction.")
        return PartialInternalState()

    job_description = state.job_description
    if not job_description:
        logger.warning("job_description is empty; skipping extraction.")
        return PartialInternalState()

    experience = state.experience.get(exp_id)
    if experience is None or not getattr(experience, "content", None):
        logger.warning(
            "Experience not found or has no content; skipping extraction. exp_id=%s", exp_id
        )
        return PartialInternalState()

    # Prepare inputs
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
        logger.exception("Failed to extract skills and accomplishments: %s", exc)
        return PartialInternalState()

    validated = NodeOutput.model_validate(result)
    saa = SkillsAndAccomplishments(
        experience_id=exp_id,
        accomplishments=validated.accomplishments,
        skills=validated.skills,
    )
    return PartialInternalState(skills_and_accomplishments={exp_id: saa})


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
You are an expert resume writer. Given a job description and a single work experience, extract:

- Accomplishments: high-quality, stand-alone resume bullet points grounded ONLY in the provided experience. Favor action verbs, clear impact, and quantified results when present. Avoid fluff or unverifiable claims.
- Skills: a concise, deduplicated list of skills that the experience demonstrates and that appear in (or are clearly implied by) the job description.

Strict requirements:
- Be strictly truthful and grounded in the provided experience content. Do not invent facts.
- Prefer wording that mirrors the job description where appropriate.
- Bullets should be concise, professional, and results-oriented.
- If the experience lacks sufficient signal for a category, return an empty list for that category.

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
    """Structured result of the extraction step."""

    accomplishments: list[str] = Field(
        default_factory=list,
        description=(
            "Stand-alone resume bullet points grounded solely in the provided experience."
        ),
    )
    skills: list[str] = Field(
        default_factory=list,
        description="Skills demonstrated by the experience that align with the job description.",
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
