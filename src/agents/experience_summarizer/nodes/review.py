from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.logging_config import logger
from src.models import OpenAIModels, get_model

from ..state import ExperienceState, PartialExperienceState


def review(state: ExperienceState) -> PartialExperienceState:
    """Review the work experience."""
    logger.info("NODE: experience_summarizer.review")
    try:
        response = chain.invoke(
            {
                "job_description": state["job_description"],
                "experience": state["experience"],
                "summary": state["summary"],
            }
        )
        if response.strip() == "--EMPTY--":
            return {"summary": None}
        elif response.strip() == "--NO CHANGE--":
            return {"summary": state["summary"]}
        else:
            # TODO: Compare the size of the diff between the original and the new summary.
            # TODO: Somehow log the size of the diff as an online evaluation metric.
            # TODO: If the diff is consistently too large, or there are too many changes, the summarizer needs to be improved. This step should usually do nothing.
            return {"summary": response}
    except Exception as e:
        logger.error(f"Error summarizing experience: {e}", exc_info=True)
        raise e


review_prompt = """
You are a meticulous fact-checker. Your sole purpose is to review the provided **Summarized Experience** and ensure every statement is factually supported by the **Original Work Experience**.

**Instructions:**

1.  **Cross-Reference and Verify:** Carefully compare each sentence and claim in the **Summarized Experience** against the details provided in the **Original Work Experience**.
2.  **Strict Correction Rule:** You MUST NOT make any edits to the **Summarized Experience** unless a claim is not factually supported by the **Original Work Experience**.
    *   If a claim exaggerates, misrepresents, or fabricates information, you must correct it to be an accurate reflection of the **Original Work Experience**.
    *   If an entire summary section within the **Summarized Experience** is unsupported or fabricated, you must remove that section completely.
    *   All corrections must be strictly grounded in the details found in the **Original Work Experience** and aligned with the terminology in the **Target Job Description**.
3.  **No Trivial Edits:** DO NOT make trivial or stylistic edits. Do not rephrase sentences for flow or clarity if the original sentence is factually correct. The goal is only to correct factual inaccuracies.
4.  **Output Conditions:** Based on your verification, provide one of the following three outputs:
    *   If you make **no corrections** because all statements are factually supported, return the exact string: `--NO CHANGE--`
    *   If **all** of the provided summary sections are fabricated and cannot be corrected to align with the source material, return the exact string: `--EMPTY--`
    *   If you make any corrections, return the fully corrected work experience summary.
5.  **Final Output:** Return only one of the three possible outputs described above. Do not include any other comments, introductions, or explanations.

**Input:**

**[Target Job Description]**

{job_description}

**[Original Work Experience]**

{experience}

**[Summarized Experience to Verify]**

{summary}
"""

llm = get_model(OpenAIModels.gpt_4o_mini)
chain = ChatPromptTemplate.from_messages([("system", review_prompt)]) | llm | StrOutputParser()
