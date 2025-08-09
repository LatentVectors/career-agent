from typing import List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.core.models import OpenAIModels, get_model
from src.logging_config import logger

from ..state import InternalState, PartialInternalState, Summary


def write_cover_letter(state: InternalState) -> PartialInternalState:
    """Write a cover letter for the job."""
    logger.debug("NODE: write_cover_letter")
    word_count = 0
    character_count = 0
    if state.cover_letter:
        word_count = len(state.cover_letter.split())
        character_count = len(state.cover_letter)

    cover_letter = chain.invoke(
        {
            "job_description": state.job_description,
            "experience": format_summary(state.summarized_experience, "Experience"),
            "responses": format_summary(state.summarized_responses, "Candidate Responses"),
            "feedback": state.cover_letter_feedback,
            "current_draft": state.cover_letter,
            "word_count": word_count,
            "character_count": character_count,
        }
    )
    return PartialInternalState(cover_letter=cover_letter)


def format_summary(summaries: dict[str, List[Summary]], title_header: str) -> str:
    """Format the summary."""
    formatted_summary = ""
    for title in summaries.keys():
        formatted_summary += f"<{title_header}>{title}</{title_header}>\n"
        for summary in summaries[title]:
            formatted_summary += f"<Summary>\n{summary.summary}\n</Summary>\n"
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
