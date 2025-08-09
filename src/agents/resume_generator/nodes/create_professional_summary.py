from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.core.models import OpenAIModels, get_model
from src.logging_config import logger

from ..state import InternalState, PartialInternalState


def create_professional_summary(state: InternalState) -> PartialInternalState:
    """
    Generate a professional summary for the users resume. This summary should be grounded in the provided experience and responses summary to best align with the job description. This summary should highlight how the user is a unique candidate for the position and should avoid generic statements.

    Defer: True

    Reads:
        - job_description
        - experience_summary
        - responses_summary

    Returns:
        - professional_summary: str
    """
    logger.debug("NODE: resume_generator.create_professional_summary")

    job_description: str | None = state.job_description
    experience_summary_map: dict[int, str] = state.experience_summary or {}
    responses_summary: str | None = state.responses_summary

    # Format experience summaries for the prompt
    formatted_experience_summaries = "".join(
        f"<Experience id=\"{experience_id}\">\n{summary}\n</Experience>\n"
        for experience_id, summary in experience_summary_map.items()
    )
    if not formatted_experience_summaries:
        formatted_experience_summaries = "<Experience>None provided</Experience>\n"

    formatted_responses_summary = (
        responses_summary if responses_summary else "None provided"
    )

    result: str = summary_chain.invoke(
        {
            "job_description": job_description or "",
            "experience_summaries": formatted_experience_summaries,
            "responses_summary": formatted_responses_summary,
        }
    )

    professional_summary = result.strip()
    logger.debug("Professional summary generated (chars=%d)", len(professional_summary))

    return PartialInternalState(professional_summary=professional_summary)


system_prompt = """
You are an expert resume writer.

Task: Create a compelling professional summary tailored to the provided job description, grounded ONLY in the supplied experience summaries and responses summary.

Guidelines:
- Prioritize relevance to the target role; mirror critical terminology from the job description when justified by the candidate data.
- Be specific and avoid generic fluff. Do not invent accomplishments or experience.
- Synthesize across experiences and responses to present a coherent narrative of strengths and differentiators.
- Keep it concise: 3–5 sentences (no bullets). Use direct, professional language.
- If data is sparse, acknowledge scope implicitly by focusing on verifiable strengths without speculation.

Output: Return ONLY the summary text with no preamble or section headings.
"""

user_prompt = """
<Job Description>
{job_description}
</Job Description>

<Experience Summaries>
{experience_summaries}
</Experience Summaries>

<Responses Summary>
{responses_summary}
</Responses Summary>
"""

summary_chain = (
    ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", user_prompt),
        ]
    )
    | get_model(OpenAIModels.gpt_4o_mini)
    | StrOutputParser()
)
