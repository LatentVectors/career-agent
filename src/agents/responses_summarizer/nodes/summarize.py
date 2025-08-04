from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from src.logging_config import logger
from src.models import OpenAIModels, get_model
from src.types import RequirementSummary

from ..state import InternalState, PartialInternalState


def summarize(state: InternalState) -> PartialInternalState:
    """Summarize the responses."""
    logger.debug("NODE: responses_summarizer.summarize")
    responses = state.responses
    job_requirements = state.job_requirements
    if not responses or not job_requirements:
        logger.warning("No responses or job requirements provided.")
        return PartialInternalState(summaries=[])

    formatted_responses = ""
    for response in responses:
        formatted_responses += (
            f"[Prompt]: {response.prompt}\n[CandidateResponse]: {response.response}\n\n"
        )
    formatted_job_requirements = ""
    for key, value in job_requirements.items():
        formatted_job_requirements += f"{key}) {value}\n"

    result = chain.invoke(
        {
            "responses": formatted_responses,
            "job_requirements": formatted_job_requirements,
        }
    )
    logger.debug(f"Response: {result}")
    validated = Summaries.model_validate(result)
    source = state.source
    return PartialInternalState(
        summaries=[
            RequirementSummary(
                source=source if source else "NA",
                requirements=summary.requirements,
                summary=summary.summary,
            )
            for summary in validated.summaries
        ]
    )


system_prompt = """
You are responsible for summarizing responses from a candidate to align with a list of job requirements. The provided responses cover a variety of topics and are presented as a list of prompts and a candidate's response to the prompt. Given a list of numbered job requirements and a candidate's responses, you need to identify any job requirements where the candidate's responses align with the job requirements and write a summary of that response.

<Instructions>
- If more than one response is relevant to the job requirements, return a unique summary object for each response and reference the same requirement number in the requirement key.
- These response summaries will be referenced when writing multiple different documents as part of a the candidates job search including resumes, cover letters, LinkedIn profiles, emails, and private messages. Make sure the summaries include sufficient detail to be useful for these documents. Also, be sure to include specific words or phrases from the job requirements in the summary where appropriate. For example, if the response and job requirement both include the word "Python", include it in the summary. As another example, if the job requirement states that the company is a "fast-paced, rapidly-growing marketing startup", and the response indicates the candidate has worked in similar settings or has worked in a similar industry, be sure to include the phrases "fast-paced", "rapidly-growing", or "marketing startup" in the summary where appropriate, rather than using other more generic terms not found in the job requirements. This will help better contextualize the response in terms of the job requirements and better align with what the hiring manager is looking for.
- Sometimes a single response may relate well to multiple job requirements, in this case, include each requirement number in the requirement key. While this is an option you can use, you should strive to find a single response that is most relevant to the job requirements and include that response in a single summary object. The option to return multiple requirement numbers is mostly available for when multiple responses are highly correlated or related and a single summary would essentially result in two duplicate summaries.
- The summary should be a single, short paragraph that is related to the requirement. In some instances, only a sentence or two may be necessary. 
- You do not need to try and find a related summary for every single job requirement. By no means should you try and force the response to fit a job requirement where the response is not relevant.
- Remember all summaries may potentially be used to create documents for the candidates job search and should strive to present the candidate's response in the best way possible that can be supported by the provided response. If there are impressive or attention-grabbing details, be sure to include them in the summary. If there are metrics that quantify the candidate's impact or performance in a compelling way, be sure to include them in the summary.
- Some job requirements may not be directly stated directly as a requirement or tied to specific skills. For example, some job requirements may only mention the companies industry, the type of product they sell, or their company values. If the candidates response relates to these requirements, be sure to include a summary for them.
- Be sure that all summaries are completely truthful and grounded in the provided responses. Do not exaggerate, embellish, or invent any details. THIS IS EXTREMELY IMPORTANT! False or misleading information will result in poor outcomes for the candidate. While striving to present the candidate in the best light possible, do not ever lie, misrepresent, or exaggerate the responses.
- The summary should be written from the "I" perspective.
- Use clear, concise, professional, direct, and compelling language.
</Instructions>

<Return Format>
You should return a JSON object with a single key, summaries, which holds a list of objects. Each object should have two keys, requirement and summary. The requirement key should be the number of the requirement that the response is related to. The summary key should be a summary of the response that is related to the requirement.
If the response is completely irrelevant to the job requirements, return an empty summaries list.

</Return Format>
"""

user_prompt = """
**[Job Requirements]**
{job_requirements}

**[Candidate Responses]**
{responses}
"""


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("user", user_prompt),
    ]
)


class Summaries(BaseModel):
    """Summaries of the candidate responses matching the job requirements."""

    summaries: list[Summary] = Field(
        description="A list of summaries matching the job requirements.",
        default_factory=list,
    )


class Summary(BaseModel):
    """A summary of a requirement."""

    requirements: list[int] = Field(description="The requirements that the summary covers.")
    summary: str = Field(
        description="Summarized content drawn from the provided candidate responses."
    )


llm = get_model(OpenAIModels.gpt_4o_mini).with_structured_output(Summaries)

chain = prompt | llm
