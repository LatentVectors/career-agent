from typing import List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.logging_config import logger
from src.models import OpenAIModels, get_model
from src.state import MainState, PartialMainState, Summary


def write_cover_letter(state: MainState) -> PartialMainState:
    """Write a cover letter for the job."""
    logger.debug("NODE: write_cover_letter")
    job_description = state["job_description"]
    summaries = state["summarized_experience"]
    responses = state["summarized_responses"]
    # TODO: Why is there no key in the state? Is it because I am returning a partial state?
    feedback: str | None = state.get("cover_letter_feedback")
    current_draft: str | None = state.get("cover_letter")
    if summaries is None or responses is None:
        logger.error("Summarized experience and responses are required")
        raise ValueError("Summarized experience and responses are required")

    word_count = 0
    character_count = 0
    if current_draft:
        word_count = len(current_draft.split())
        character_count = len(current_draft)

    cover_letter = chain.invoke(
        {
            "job_description": job_description,
            "experience": format_summary(summaries, "Experience"),
            "responses": format_summary(responses, "Candidate Responses"),
            "feedback": feedback,
            "current_draft": current_draft,
            "word_count": word_count,
            "character_count": character_count,
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
- The <Draft Feedback> includes feedback on the current draft of the cover-letter, if any.
- The <Current Draft> includes the current draft of the cover-letter, if any.

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

<Draft Feedback>
{feedback}
</Draft Feedback>

<Draft Metrics>
Word Count: {word_count}
Character Count: {character_count}
</Draft Metrics>

<Current Draft>
{current_draft}
</Current Draft>
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
