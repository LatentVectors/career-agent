from __future__ import annotations

from typing import List

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from src.core.models import OpenAIModels, get_model
from src.logging_config import logger

from ..state import InternalState, PartialInternalState, Summary


def write_resume(state: InternalState) -> PartialInternalState:
    """Write a resume based on job description, summarized experience, and responses."""
    logger.debug("NODE: write_resume")

    resume_content = chain.invoke(
        {
            "job_description": state.job_description,
            "experience": format_summary(state.summarized_experience, "Experience"),
            "responses": format_summary(state.summarized_responses, "Candidate Responses"),
        }
    )

    # Convert the structured resume content to a formatted string
    formatted_resume = format_resume_content(resume_content)

    return PartialInternalState(resume=formatted_resume)


def format_summary(summaries: dict[str, List[Summary]], title_header: str) -> str:
    """Format the summary for the prompt."""
    formatted_summary = ""
    for title in summaries.keys():
        formatted_summary += f"<{title_header}>{title}</{title_header}>\n"
        for summary in summaries[title]:
            formatted_summary += f"<Summary>\n{summary.summary}\n</Summary>\n"
    return formatted_summary


def format_resume_content(resume: ResumeContent) -> str:
    """Format the structured resume content into a readable string format."""
    lines = []

    # Contact Information
    contact = resume.metadata.contact_info
    lines.append(f"{contact.get('name', '')}")
    lines.append(f"{contact.get('email', '')} | {contact.get('phone', '')}")
    lines.append(f"{contact.get('location', '')}")
    if resume.metadata.linkedin_url:
        lines.append(f"LinkedIn: {resume.metadata.linkedin_url}")
    if resume.metadata.github_url:
        lines.append(f"GitHub: {resume.metadata.github_url}")
    if resume.metadata.portfolio_url:
        lines.append(f"Portfolio: {resume.metadata.portfolio_url}")
    lines.append("")

    # Professional Summary
    lines.append("PROFESSIONAL SUMMARY")
    lines.append("=" * 50)
    lines.append(resume.summary.overview)
    lines.append("")

    # Key Highlights
    if resume.summary.key_highlights:
        lines.append("KEY HIGHLIGHTS")
        lines.append("-" * 30)
        for highlight in resume.summary.key_highlights:
            lines.append(f"• {highlight}")
        lines.append("")

    # Skills
    if resume.skills:
        lines.append("SKILLS")
        lines.append("=" * 50)
        # Group skills by category
        skills_by_category: dict[str, list[ResumeSkill]] = {}
        for skill in resume.skills:
            if skill.category not in skills_by_category:
                skills_by_category[skill.category] = []
            skills_by_category[skill.category].append(skill)

        for category, skills in skills_by_category.items():
            lines.append(f"{category.upper()}:")
            skill_names = [f"{skill.name} ({skill.proficiency_level})" for skill in skills]
            lines.append(", ".join(skill_names))
        lines.append("")

    # Experience
    if resume.experience:
        lines.append("PROFESSIONAL EXPERIENCE")
        lines.append("=" * 50)
        for exp in resume.experience:
            lines.append(f"{exp.title}")
            lines.append(f"{exp.company} | {exp.duration}")
            lines.append("")
            lines.append(exp.description)
            lines.append("")
            if exp.key_achievements:
                lines.append("Key Achievements:")
                for achievement in exp.key_achievements:
                    lines.append(f"• {achievement}")
                lines.append("")
            if exp.technologies:
                lines.append(f"Technologies: {', '.join(exp.technologies)}")
            lines.append("-" * 40)
            lines.append("")

    # Education
    if resume.metadata.education:
        lines.append("EDUCATION")
        lines.append("=" * 50)
        for edu in resume.metadata.education:
            lines.append(f"{edu.get('degree', '')}")
            lines.append(f"{edu.get('institution', '')} | {edu.get('year', '')}")
            if edu.get("gpa"):
                lines.append(f"GPA: {edu.get('gpa')}")
            lines.append("")

    # Certifications
    if resume.metadata.certifications:
        lines.append("CERTIFICATIONS")
        lines.append("=" * 50)
        for cert in resume.metadata.certifications:
            lines.append(f"• {cert}")
        lines.append("")

    # Languages
    if resume.metadata.languages:
        lines.append("LANGUAGES")
        lines.append("=" * 50)
        lines.append(", ".join(resume.metadata.languages))
        lines.append("")

    # Additional sections
    for section_name, section_content in resume.additional_sections.items():
        lines.append(section_name.upper())
        lines.append("=" * 50)
        if isinstance(section_content, list):
            for item in section_content:
                lines.append(f"• {item}")
        else:
            lines.append(str(section_content))
        lines.append("")

    return "\n".join(lines)


system_prompt = """
You are an expert resume writer. Your task is to create a comprehensive, professional resume based on the provided job description, candidate experience, and candidate responses.

The resume should be tailored to the specific job description and highlight relevant experience and skills. Use the candidate's experience and responses to create compelling content that demonstrates their qualifications for the target role.

IMPORTANT: Return the resume content as a structured JSON object that matches the ResumeContent schema. The response should be valid JSON that can be parsed into the ResumeContent model.

Guidelines for creating the resume:
1. Extract relevant contact information from the experience and responses
2. Create a compelling professional summary that aligns with the job requirements
3. Format experience entries with clear job titles, companies, durations, and achievements
4. Organize skills by category (Technical, Soft Skills, etc.) with proficiency levels
5. Include education, certifications, and languages if mentioned
6. Focus on achievements and quantifiable results
7. Use action verbs and industry-specific terminology
8. Ensure all content is truthful and based on the provided information
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

Please create a comprehensive resume that:
- Is tailored to the job description
- Highlights relevant experience and skills
- Uses professional formatting
- Includes all necessary sections (contact, summary, experience, skills, education, etc.)
- Demonstrates the candidate's qualifications for the target role

Return the resume as a structured ResumeContent object in JSON format.
"""


class ResumeExperience(BaseModel):
    """A single experience entry for the resume."""

    title: str = Field(description="Job title or role")
    company: str = Field(description="Company or organization name")
    duration: str = Field(
        description="Duration of employment (e.g., '2020-2023' or 'Jan 2020 - Present')"
    )
    description: str = Field(
        description="Detailed description of responsibilities and achievements"
    )
    key_achievements: List[str] = Field(description="List of key achievements or accomplishments")
    technologies: List[str] = Field(description="Technologies, tools, or skills used in this role")


class ResumeSkill(BaseModel):
    """A skill entry for the resume."""

    name: str = Field(description="Name of the skill")
    category: str = Field(
        description="Category of the skill (e.g., 'Technical', 'Soft Skills', 'Languages')"
    )
    proficiency_level: str = Field(
        description="Proficiency level (e.g., 'Expert', 'Advanced', 'Intermediate', 'Beginner')"
    )
    years_of_experience: int = Field(description="Years of experience with this skill")


class ResumeSummary(BaseModel):
    """Professional summary for the resume."""

    overview: str = Field(description="Professional overview and career objective")
    key_highlights: List[str] = Field(description="Key highlights or selling points")
    target_role: str = Field(description="Target role or position being sought")


class ResumeMetadata(BaseModel):
    """Metadata for the resume."""

    contact_info: dict = Field(description="Contact information (name, email, phone, location)")
    education: List[dict] = Field(description="Education background")
    certifications: List[str] = Field(description="Professional certifications")
    languages: List[str] = Field(description="Languages spoken")
    linkedin_url: str | None = Field(default=None, description="LinkedIn profile URL")
    github_url: str | None = Field(default=None, description="GitHub profile URL")
    portfolio_url: str | None = Field(default=None, description="Portfolio website URL")


class ResumeContent(BaseModel):
    """Complete resume content structure."""

    metadata: ResumeMetadata = Field(
        description="Resume metadata including contact info and education"
    )
    summary: ResumeSummary = Field(description="Professional summary and highlights")
    experience: List[ResumeExperience] = Field(description="Work experience entries")
    skills: List[ResumeSkill] = Field(description="Skills and competencies")
    additional_sections: dict = Field(
        default_factory=dict, description="Any additional sections like projects, awards, etc."
    )


llm = get_model(OpenAIModels.gpt_4o)
parser = PydanticOutputParser(pydantic_object=ResumeContent)

chain = (
    ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", user_prompt),
        ]
    )
    | llm
    | parser
)
