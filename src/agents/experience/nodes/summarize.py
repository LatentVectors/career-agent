from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.logging_config import logger
from src.models import llm_with_retry

from ..state import ExperienceState, PartialExperienceState


def summarize(state: ExperienceState) -> PartialExperienceState:
    """Summarize the work experience."""
    logger.info("Summarizing Experience")
    try:
        response = chain.invoke(
            {
                "job_description": state["job_description"],
                "experience": state["experience"],
            }
        )
        if response.strip() == "--EMPTY--":
            return {"summary": None}
        else:
            return {"summary": response}
    except Exception as e:
        logger.error(f"Error summarizing experience: {e}", exc_info=True)
        raise e


# TODO: Include the position(s)/role(s) held.
# TODO: Include the company(ies) worked for.
# TODO: Include the location(s) of the work experience.
# TODO: Include the dates and duration of the work experience.
# TODO: Inject the current date into the prompt.
# TODO: Include tools for calculating the duration between two dates.
# TODO: Include the type of work experience (full-time, part-time, internship, etc.).
# TODO: Include the industry of the work experience.
# TODO: Include a short description of the company.
# TODO: Specify a more specific structure for the returned summary.
# TODO: Potentially provide a few examples to the prompt using few-shot prompting.
# TODO: Consider using structured output to ensure the summary is in the correct format.

summary_prompt = """
You are an expert in career coaching and resume writing. Your task is to analyze the provided **Work Experience** and **Target Job Description**. Based on this analysis, you will write a concise and impactful summary of the work experience that is tailored to the target job description.

**Instructions:**

1.  **Analyze the Target Job Description:** Carefully read the **Target Job Description** to identify the key requirements, responsibilities, and qualifications. Pay close attention not only to explicit keywords, technologies, and skills but also to the implied behavioral traits, soft skills (e.g., communication, teamwork), and competencies (e.g., problem-solving, leadership) the role requires.

2.  **Analyze the Work Experience:** Thoroughly review the provided **Work Experience**. Your goal is to identify all experiences, accomplishments, and skills that are relevant to the **Target Job Description**. Look beyond direct parallels and identify demonstrated evidence of:
    *   Relevant technical and project management skills.
    *   Relevant problem-solving, leadership, communication, and team skills.
    *   Underlying aptitudes, temperamental traits, or competencies that translate to the requirements of the target job.

3.  **Summarize Relevant Experience:**
    *   If the provided **Work Experience** is completely irrelevant to the **Target Job Description** and no transferable skills can be honestly identified, return the exact string `--EMPTY--` and nothing else.
    *   Otherwise, for each relevant project, role, or accomplishment, write a summary that highlights its connection to the **Target Job Description**.

4.  **Summary Guidelines:**
    *   **Use the First Person:** Write the summary from the "I" perspective.
    *   **Focus on Alignment:** Directly address the requirements of the target role. Use the language and keywords from the job description where appropriate and justified by the experience. Weave in the transferable soft skills and competencies you identified.
    *   **Be Factual and Grounded:** Do not exaggerate, embellish, or invent any details. The summary must be a truthful representation of the provided work experience.
    *   **Apply the STAR Method (where applicable):** If the experience allows, structure the summary using the STAR method (Situation, Task, Action, Result) to clearly demonstrate impact.
    *   **Contextualize Numbers:** When using numbers to quantify impact, consider the scale and context. A $10,000 cost savings for a department with a $15,000 budget is highly significant.
    *   **Professional Tone:** Use clear, direct, and professional language. Avoid jargon unless it is a key term from the job description.
    *   **Separate Summaries:** If the work experience contains multiple relevant examples, create a separate summary for each. Each summary should be one to two short paragraphs.
    *   **Output:** Return only the summarized experience. Do not include any introductory phrases, commentary, or any text other than the summaries themselves.

**Input:**

**[Target Job Description]**

{job_description}

**[Work Experience]**

{experience}{experience}
"""

chain = (
    ChatPromptTemplate.from_messages([("system", summary_prompt)])
    | llm_with_retry
    | StrOutputParser()
)
