from typing import List

from langchain_core.prompts.chat import ChatPromptTemplate
from openai import APIConnectionError
from pydantic import BaseModel, Field

from src.logging_config import logger
from src.models import OpenAIModels, get_model

from ..state import MainState, PartialMainState


class JobRequirements(BaseModel):
    requirements: List[str] = Field(description="A list of requirements for the job.")


def get_job_requirements(state: MainState) -> PartialMainState:
    """Extract job requirements from a job description."""
    logger.info("NODE: get_job_requirements")
    job_description = state["job_description"]
    response = chain.invoke({"job_description": job_description})
    requirements = JobRequirements.model_validate(response)
    job_requirements = {}
    for i, requirement in enumerate(requirements.requirements):
        job_requirements[i + 1] = requirement
    return {"job_requirements": job_requirements}


system_prompt = """
You are responsible for extracting job requirements or important context from job descriptions. The list of excerpts you extract will be used to tailor resume, cover letters, interview answers, emails, and other documents for a candidate applying to this job. Each excerpt should be a single, complete statement taken from the job description, with as little editing as possible. Typically, this will be a single sentence, phrase, or bullet point from the job description.
Remember that these excerpts will be use to tailor a number of different documents as part of the candidates application process, and not just writing the resume. As such, content related to the company culture, mission, values, team environment, and work style is just as important as the lists of responsibilities and qualifications. 
Some content is less relevant to the candidate's alignment with a given position, team, or company, such as equal opportunity statements, diversity statements, vacation policies, or any other generic information related to the company or its policies. Do not include this content in your output.
Each excerpt should should be a single, clearly defined statement. Do not include multiple statements in a single excerpt.
Each extracted excerpt should be strictly grounded in the provided job description. Do not invent, add, extrapolate, or embellish any information that is not explicitly present in the text. If summarization is necessary to preserve the meaning or context of the excerpt, be sure to maintain the original words or phrases as much as possible, since ATS systems, HR professionals, and hiring managers will likely look for these exact words or phrases in resumes, cover letters, and interview answers. Some summarization is acceptable, but only if it is necessary to preserve the meaning or context of the excerpt.
Be thorough and extract all relevant information from the job description. Do not miss any important details or statements about the job, company, team, candidate temperament, technical skills, work culture, work style, industry, or any other relevant information that could be useful in tailoring a resume, cover letter, interview answers, emails, and other documents for a candidate applying to this job. Consider all parts of the provided job description when searching for relevant excerpts. Remember, the job title is an important piece of information that should be included in the output, if present in the job description.
If a requirement, qualification, or other excerpt is described with a specific term like 'required,' 'minimum,' 'must-have,' 'preferred,' 'plus,' 'nice-to-have,' etc., append that exact term in parentheses to the end of the extracted string. For example, "5+ years experience with ADO (Minimum)" or "Strong communication skills (Required)". This includes any items that are explicitly stated as disqualifier's such as "Lives outside of the United States (Disqualifier)" or "Does not have an advanced degree (Disqualifier)".
Return the output as a JSON object with a single key, requirements, which holds a list of strings. Each string in the list must be a single, distinct point of information extracted according to the principles above. If the job description is empty or the provided document is not a job description, return an empty list.
"""

user_prompt = """
**[Job Description]**

{job_description}
"""


llm = get_model(OpenAIModels.gpt_4o_mini)
llm_with_structured_output = llm.with_structured_output(JobRequirements).with_retry(
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
