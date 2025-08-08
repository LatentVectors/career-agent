from __future__ import annotations

from langchain_core.prompts.chat import ChatPromptTemplate
from langgraph.runtime import Runtime
from openai import APIConnectionError
from pydantic import BaseModel, Field

from src.context import AgentContext
from src.logging_config import logger
from src.models import OpenAIModels, get_model

from ..state import InternalState, PartialInternalState


class JobMetadata(BaseModel):
    job_title: str = Field(description="The primary job title extracted from the job description.")
    company_name: str | None = Field(
        default=None, description="The company name if mentioned in the job description."
    )
    location: str | None = Field(
        default=None, description="The job location if mentioned in the job description."
    )


def extract_job_metadata(
    state: InternalState,
    runtime: Runtime[AgentContext],
) -> PartialInternalState:
    """Extract job title and metadata from a job description."""
    logger.debug("NODE: extract_job_metadata")
    logger.debug(f"State Type: {type(state)}")
    job_description = state.job_description
    response = chain.invoke({"job_description": job_description})
    metadata = JobMetadata.model_validate(response)
    return PartialInternalState(job_title=metadata.job_title)


system_prompt = """
You are responsible for extracting the primary job title and key metadata from job descriptions. Your task is to identify the most relevant and specific job title that would be used in professional contexts.

Guidelines for job title extraction:
1. Look for the most specific and descriptive job title mentioned in the job description
2. If multiple titles are mentioned, select the most likely primary title (usually mentioned first or most prominently)
3. Prefer more specific titles over generic ones (e.g., "Senior Software Engineer" over "Engineer")
4. If the job description doesn't clearly state a title, infer the most appropriate title based on the responsibilities and requirements
5. Avoid titles that are too generic or vague
6. If there are multiple similar titles, choose the one that best matches the level and responsibilities described

Additional metadata to extract if available:
- Company name (if mentioned)
- Job location (if mentioned)

Return the output as a JSON object with the following structure:
- job_title: The primary job title (required)
- company_name: The company name if mentioned (optional)
- location: The job location if mentioned (optional)

If the job description is empty or doesn't contain a clear job title, return a reasonable default title based on the content.
"""

user_prompt = """
**[Job Description]**

{job_description}
"""


llm = get_model(OpenAIModels.gpt_4o_mini)
llm_with_structured_output = llm.with_structured_output(JobMetadata).with_retry(
    retry_if_exception_type=(APIConnectionError,)
)

chain = (
    ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", user_prompt),
        ]
    )
    | llm_with_structured_output
)
