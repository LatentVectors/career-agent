from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.logging_config import logger
from src.models import OpenAIModels, get_model
from src.state import MainState, PartialMainState


def write_cover_letter(state: MainState) -> PartialMainState:
    """Write a cover letter for the job."""
    logger.info("Writing cover letter...")
    logger.info(f"State: {state}")
    for key, value in state.items():
        logger.info(f"{key}: {str(value)[:50]}...")
    job_description = state["job_description"]
    summaries = state["summarized_experience"]
    if summaries is None:
        raise ValueError("Summarized experience is required")

    experience = ""
    for title in summaries.keys():
        experience += f"<Experience Title>{title}</Experience Title>\n"
        for summary in summaries[title]:
            content = summary["summary"]
            experience += f"<Summary>\n{content}\n</Summary>\n"
        experience += "\n"

    cover_letter = chain.invoke(
        {
            "job_description": job_description,
            "experience": experience,
        }
    )
    return {"cover_letter": cover_letter}


system_prompt = """
You are responsible for writing a high-quality cover-letter based on the provided job description and experience.

<Response>
Only return the text for the cover-letter. Do not include any additional commentary or content.
</Response>
"""

user_prompt = """
<Job Description>
{job_description}
</Job Description>

<Experience>
{experience}
</Experience>
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
