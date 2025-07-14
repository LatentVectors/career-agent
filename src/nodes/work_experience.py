from typing import List

from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from pydantic.main import BaseModel

from ..logging_config import logger
from ..state import ExperienceSummary, ReturnState, State
from .models import llm_with_retry


def summarize_experience(state: State) -> ReturnState:
    """Summarize the work experience."""
    logger.info("Summarizing Experience")
    summarized_experiences: List[ExperienceSummary] = []
    try:
        for experience in state["background"]["experience"]:
            logger.info(f"- Experience: {experience.title}")
            job_description = state["job"].description
            experience_content = experience.content
            logger.debug(f"Job Description: {job_description[:100]}...")
            logger.debug(f"Experience: {experience_content[:100]}...")
            response = chain.invoke(
                {
                    "job_description": job_description,
                    "experience": experience,
                }
            )
            logger.debug(f"Response: {response[:100]}...")
            summarized_experiences.append(
                ExperienceSummary(
                    source=experience.title,
                    experience=response,
                )
            )
        logger.debug(f"Summarized {len(summarized_experiences)} experiences")
        return {"experience": summarized_experiences}
    except Exception as e:
        logger.error(f"Error summarizing experience: {e}", exc_info=True)
        raise e


summarize = (
    ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are a helpful assistant that summarizes work experience.
""",
            ),
            (
                "human",
                """
Job Description:
{job_description}

Experience:
{experience}

Summarize the experience in terms of the job description.
     """,
            ),
        ]
    )
    | llm_with_retry
    | StrOutputParser()
)

review = (
    ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant that reviews work experience."),
            (
                "human",
                "Job Description: {job_description}\n\nExperience: {experience}\n\nReview the experience in terms of the job description. {summary}",
            ),
        ]
    )
    | llm_with_retry
    | StrOutputParser()
)


class ExperienceSummaryInput(BaseModel):
    job_description: str
    experience: str


chain = RunnablePassthrough(input_type=ExperienceSummaryInput).assign(summary=summarize) | review
