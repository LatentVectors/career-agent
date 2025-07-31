from typing import List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.logging_config import logger
from src.models import OpenAIModels, get_model
from src.state import MainState, PartialMainState, Summary


def write_cover_letter(state: MainState) -> PartialMainState:
    """Write a cover letter for the job."""
    logger.info("NODE: write_cover_letter")
    job_description = state["job_description"]
    summaries = state["summarized_experience"]
    responses = state["summarized_responses"]
    if summaries is None or responses is None:
        logger.error("Summarized experience and responses are required")
        raise ValueError("Summarized experience and responses are required")

    cover_letter = chain.invoke(
        {
            "job_description": job_description,
            "experience": format_summary(summaries, "Experience"),
            "responses": format_summary(responses, "Candidate Responses"),
        }
    )
    return {"cover_letter": cover_letter}


def format_summary(summaries: dict[str, List[Summary]], title_header: str) -> str:
    """Format the summary."""
    formatted_summary = ""
    for title in summaries.keys():
        formatted_summary += f"<{title_header}>{title}</{title_header}>\n"
        for summary in summaries[title]:
            content = summary["summary"]
            formatted_summary += f"<Summary>\n{content}\n</Summary>\n"
    return formatted_summary


system_prompt = """
You are responsible for writing a high-quality cover-letter based on the provided <Job Description> and <Candidate Experience> and <Candidate Responses>.

- The <Job Description> describes the job the candidate is applying for.
- The <Candidate Experience> includes summaries based on the candidate's experience.
- The <Candidate Responses> includes summaries based on the candidate's responses to various, career-related prompts.

<Response>
Only return the text for the cover-letter. Do not include any additional commentary or content.
</Response>
"""

user_prompt = """
<Job Description>
{job_description}
</Job Description>

<Candidate Experience>
{experience}
</Candidate Experience>

<Candidate Responses>
{responses}
</Candidate Responses>
"""

llm = get_model(OpenAIModels.gpt_3_5_turbo)
chain = (
    ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", user_prompt),
        ]
    )
    | llm
    | StrOutputParser()
)
