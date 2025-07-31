from __future__ import annotations

from typing import List

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from src.logging_config import logger
from src.models import OpenAIModels, get_model

from ..state import ExperienceState, ExperienceSummary, PartialExperienceState


def summarize(state: ExperienceState) -> PartialExperienceState:
    """Summarize the work experience."""
    logger.info("NODE: experience_summarizer.summarize")
    requirements = state["job_requirements"]
    if requirements is None or len(requirements) == 0:
        logger.warning("No job requirements found. Returning empty summary.")
        return {"summary": None}
    try:
        job_requirements = ""
        for key, value in requirements.items():
            job_requirements += f"{key}) {value}\n"
        experience = state["experience"]
        response = chain.invoke(
            {
                "job_requirements": job_requirements,
                "experience": experience,
                "output_example": output_example,
            }
        )
        validated = Summary.model_validate(response).experience_summaries
        summary: List[ExperienceSummary] = [
            {
                "requirement": v.requirement,
                "summary": v.summary,
            }
            for v in validated
        ]
        if len(summary) == 0:
            logger.info("No summaries found. Returning empty summary.")
            return {"summary": None}
        return {"summary": summary}
    except Exception as e:
        logger.error(f"Error summarizing experience: {e}", exc_info=True)
        raise e


class Summary(BaseModel):
    """The summary of the work experience."""

    experience_summaries: List[Experience] = Field(
        description="The summaries of the work experience.",
        default_factory=list,
    )


class Experience(BaseModel):
    """The summary of the work experience."""

    requirement: List[int] = Field(
        description="The related job requirements the experience aligns with. This must include at least one related requirement number.",
        min_length=1,
    )

    summary: str = Field(description="The summary of the work experience.")


summary_prompt = """
You are responsible for summarizing work experience to align with a list of job requirements. Given a list of numbered job requirements and a candidate's experience, you need to identify any job requirements where the candidate has relevant experience and write a summary of that experience.

<Instructions>
- If more than one experience in the experience is relevant to the job requirements, return a unique summary object for each experience and reference the same requirement number in the requirement key.
- These experience summaries will be referenced when writing multiple different documents as part of a the candidates job search including resumes, cover letters, LinkedIn profiles, emails, and private messages. Make sure the summaries include sufficient detail to be useful for these documents. Also, be sure to include specific words or phrases from the job requirements in the summary where appropriate. For example, if the experience and job requirement both include the word "Python", include it in the summary. As another example, if the job requirement states that the company is a "fast-paced, rapidly-growing marketing startup", and the experience indicates the candidate has worked in similar settings or has worked in a similar industry, be sure to include the phrases "fast-paced", "rapidly-growing", or "marketing startup" in the summary where appropriate, rather than using other more generic terms not found in the job requirements. This will help better contextualize the experience in terms of the job requirements and better align with what the hiring manager is looking for.
- Sometimes a single experience may relate well to multiple job requirements, in this case, include each requirement number in the requirement key. While this is an option you can use, you should strive to find a single experience that is most relevant to the job requirements and include that experience in a single summary object. The option to return multiple requirement numbers is mostly available for when multiple experiences are highly correlated or related and a single summary would essentially result in two duplicate summaries.
- The summary should be a single, short paragraph that is related to the requirement. 
- You do not need to try and find a related summary for every single job requirement. By no means should you try and force the experience to fit a job requirement where the experience is not relevant.
- If appropriate and the experience include sufficient relevant details, strive to include enough information to create a STAR (Situation, Task, Action, Result) summary of the experience. If some STAR information is missing, include as much of it as you can to create this type of STAR summary.
- Not all job requirements need to be in STAR format. For example, if the job requirement only includes has Level 2 Security Clearance, you do not need to include a STAR summary, just provide a clear summary that indicates the candidate has sufficient security clearance.
- Remember all summaries may potentially be used to create documents for the candidates job search and should strive to present the candidate's experience in the best way possible that can be supported by the provided experience. If there are impressive or attention-grabbing details, be sure to include them in the summary. If there are metrics that quantify the candidate's impact or performance in a compelling way, be sure to include them in the summary.
- Some job requirements may not be directly stated directly as a requirement or tied to specific skills. For example, some job requirements may only mention the companies industry, the type of product they sell, or their company values. If the candidates experience relates to these requirements, be sure to include a summary for them.
- Be sure that all summaries are completely truthful and grounded in the provided experience. Do not exaggerate, embellish, or invent any details. THIS IS EXTREMELY IMPORTANT! False or misleading information will result in poor outcomes for the candidate. While striving to present the candidate in the best light possible, do not ever lie, misrepresent, or exaggerate the experience.
- The summary should be written from the "I" perspective.
- Use clear, concise, professional, direct, and compelling language.
</Instructions>

<Return Format>
You should return a JSON object with a single key, experience_summaries, which holds a list of objects. Each object should have two keys, requirement and summary. The requirement key should be the number of the requirement that the work experience is related to. The summary key should be a summary of the work experience that is related to the requirement.
If the experience is completely irrelevant to the job requirements, return an empty experience_summaries list.

<Example>
{output_example}
</Example>
</Return Format>
"""

output_example = """
{
    "experience_summaries": [
        {
            "requirement": [1, 2, 7],
            "summary": "I have 5 years of experience in Python and Django. At my previous job, I was responsible for independently developing and maintaining a content management app for mid-sized bloggers and social media influencers that grew to 100,000 monthly active users. I have extensively worked with the Django ORM, Django REST framework, and Django Channels to build a real-time chat application that allows users to communicate with each other in real-time. Following development, I was responsible for deploying the application to AWS and managing the application's infrastructure. Using best practices, I was responsible for CI/CD, pipelines, version control using Git, and testing using pytest. I was also responsible for training and mentoring junior developers on the team."
        },
        {
            "requirement": [3],
            "summary": "I thrive in a fast-paced environment and am a self-starter. I was employee number 3 at a startup that grew to 100 employees in 3 years and was responsible for building the companies development culture and team."
        }
        {
            "requirement": [20],
            "summary": "I have extensive experience with consumer packaged goods and large retail. As an independent consultant, I worked with Costco to develop a custom supply chain solution for their private label products. I delivered the project 2 months ahead of schedule and 34 percent under budget."
        },
        {
            "requirement": [20],
            "summary": "Previously I worked at a Walmart distribution center as an assistant logistics manager, responsible for daily operations including order fulfillment, routing, and coordinating with the Walmart distribution centers. I gained an in-depth understanding of retail supply chains and operations and logistics.
        },
        {
            "requirement": [22],
            "summary": "I am a quick learner and am able to pick up new technologies and tools quickly. I learned React and Next.js in two weeks to build a new website for a client."
        }
    ]
}
"""

user_prompt = """
**[Job Requirements]**

{job_requirements}

---

**[Work Experience]**

{experience}
"""

llm = get_model(OpenAIModels.gpt_4o_mini).with_structured_output(Summary)
chain = ChatPromptTemplate.from_messages([("system", summary_prompt), ("user", user_prompt)]) | llm
