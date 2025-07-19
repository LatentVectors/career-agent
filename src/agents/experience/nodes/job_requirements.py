from typing import List

from langchain.chat_models import init_chat_model
from langchain_core.prompts.chat import ChatPromptTemplate
from openai import APIConnectionError
from pydantic import BaseModel, Field

from src.logging_config import logger

from ..state import ExperienceState, PartialExperienceState


class JobRequirements(BaseModel):
    requirements: List[str] = Field(description="A list of requirements for the job.")


def get_job_requirements(state: ExperienceState) -> PartialExperienceState:
    """Extract job requirements from a job description."""
    logger.info("Getting job requirements")
    job_description = state["job_description"]
    response = chain.invoke({"job_description": job_description})
    logger.info(f"Job requirements response: {response}")
    requirements = JobRequirements.model_validate(response)
    job_requirements = {}
    for i, requirement in enumerate(requirements.requirements):
        job_requirements[str(i)] = requirement
    logger.info(f"Job requirements: {job_requirements}")
    return {"job_requirements": job_requirements}


prompt = """
You are an expert career assistant. Your task is to analyze the following job description and extract a comprehensive, itemized list of all requirements for the ideal candidate.

**Instructions:**

1.  **Extract All Requirement Types:** Scrutinize the text for every type of requirement, including but not limited to:
    *   Hard skills (e.g., Python, financial modeling)
    *   Soft skills (e.g., communication, leadership, collaboration)
    *   Technologies, platforms, and tools (e.g., AWS, Salesforce, Jira)
    *   Industry and domain experience (e.g., 5+ years in fintech, background in healthcare)
    *   Specific roles and responsibilities (e.g., "manage a cross-functional team," "own the product roadmap")
    *   Day-to-day tasks (e.g., "perform data analysis," "write technical documentation")
    *   Temperament, work style, and personality traits (e.g., "thrives in a fast-paced environment," "a self-starter," "meticulous attention to detail")
    *   Motivations, values, and interests (e.g., "passion for our mission," "a desire for continuous learning")
    *   Business knowledge (e.g., "experience with B2B SaaS models," "understanding of go-to-market strategies")
    *   Educational qualifications and certifications.
    *   Any other factor that would be significant in choosing one candidate over another.

2.  **Preserve Original Wording:** This is the most important rule. You must use the **exact words and phrases** from the job description as much as possible. The extracted list will be used to tailor resumes and cover letters, so it must mirror the employer's language.

3.  **Minimal Editing for Clarity:** You may perform minimal edits **only** to ensure the requirement makes sense as a standalone list item and to preserve its context. For example, if the source says, "In this role, you will be responsible for developing new features," you can extract it as "Responsible for developing new features" or "Developing new features." Do not add words or rephrase the core requirement. Be sure to include important details about the requirement, like if it is preferred, required, a nice-to-have, or a disqualifier. 

4.  **Format:** Return the output as a list of strings with one string per requirement. 

Analyze the job description below and provide only the extracted list of requirements.

---

**[Job Description]**

{job_description}

"""


llm = init_chat_model("gpt-4o-mini")
llm_with_structured_output = llm.with_structured_output(JobRequirements).with_retry(
    retry_if_exception_type=(APIConnectionError,)
)

chain = ChatPromptTemplate.from_template(prompt) | llm_with_structured_output
