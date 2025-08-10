from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.core.models import OpenAIModels, get_model
from src.logging_config import logger

from ..state import InternalState, PartialInternalState


def summarize_responses(state: InternalState) -> PartialInternalState:
    """
    Summarize free-form candidate responses in the context of the job description.

    Design contract
    - Purpose: Produce a concise, high-signal summary from `candidate_responses` that highlights how the
      candidate aligns with the target `job_description`, especially on less-tangible dimensions (e.g.,
      strengths, interests, work-style, values, motivations).
    - Inputs available when invoked:
      - job_description: str (required by design; assumed present in agent flow)
      - candidate_responses: list[CandidateResponse] (may be empty)
    - Behavior:
      - If `candidate_responses` is empty or missing, return an empty string for `responses_summary`.
      - Otherwise, format each response with its originating prompt and provide them, along with the
        job description, to the LLM using a clear prompt.
      - The LLM output must be a single, concise summary in the first person, grounded strictly in the
        provided responses. Prefer language/phrases from the job description where appropriate.
      - Use clear, professional tone; avoid generic fluff and ungrounded claims.
    - Output:
      - responses_summary: str (never None; empty string if no inputs)

    Implementation checklist
    - [x] Log node start for observability.
    - [x] Handle empty/missing candidate responses safely.
    - [x] Format inputs with [Prompt]/[Response] blocks.
    - [x] LLM call via shared model utility using ChatPromptTemplate + StrOutputParser.
    - [x] Return PartialInternalState with `responses_summary`.
    """
    logger.debug("NODE: resume_generator.summarize_responses")

    responses = state.candidate_responses or []
    if len(responses) == 0:
        logger.warning("No candidate responses provided. Returning empty responses_summary.")
        return PartialInternalState(responses_summary="")

    formatted_responses = "".join(
        f"[Prompt]: {r.prompt}\n[Response]: {r.response}\n\n" for r in responses
    )

    summary = chain.invoke(
        {
            "job_description": state.job_description,
            "responses": formatted_responses,
        }
    )

    return PartialInternalState(responses_summary=summary)


system_prompt = """
You are summarizing a candidate's responses to align with a target job description.

Guidelines
- Write in the first person ("I" voice), concise, professional, and specific.
- Ground strictly in the provided responses; do not invent details.
- Prefer language/phrases that appear in the job description where appropriate.
- Emphasize less-tangible strengths (e.g., work style, values, motivation, interests) and how they
  align with the role/company, while incorporating concrete evidence from the responses when available.
- Avoid generic fluff; focus on distinctive, high-signal points.

Return
- Only return the summary text (a short paragraph of 4–8 sentences). Do not include extra commentary.
"""

user_prompt = """
<Job Description>
{job_description}
</Job Description>

<Candidate Responses>
{responses}
</Candidate Responses>
"""

llm = get_model(OpenAIModels.gpt_3_5_turbo)
chain = (
    ChatPromptTemplate.from_messages([("system", system_prompt), ("user", user_prompt)])
    | llm
    | StrOutputParser()
)
