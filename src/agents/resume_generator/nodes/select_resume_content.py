from __future__ import annotations

from datetime import date
from typing import Final

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from src.core.models import OpenAIModels, get_model
from src.features.resume.types import (
    ResumeCertification,
    ResumeData,
    ResumeEducation,
    ResumeExperience,
)
from src.logging_config import logger

from ..state import InternalState, PartialInternalState


def select_resume_content(state: InternalState) -> PartialInternalState:
    """
    Review the generated resume content and select the most compelling experience, skills, and accomplishments to include in the final resume. If provided take into account the feedback, previous content, page length, and word count to refine the resume to meet the target page count. Beyond filtering experience, minor editing of accomplishments and refinement of the professional summary may also be used to generate the strongest possible resume for the target job description. This node uses an LLM to select the content.

    This node is currently trying to select resume content via some kind of logic flow. However, it should use an LLM to select the most compelling content. That LLM should use strucutred outputs to return the selected experience bullet points, the selected skills, and the professional summary. The structured output should include the experience_id with its related bullet points for each selected experience. The LLM can choose not to include experience if it feels it does not strengthen the resume for the target job description. If that is the case it should not include an entry for the experience in the returned content. The structured output should return the skills as an array of strings. The structured output should also include the professional_summary in the structured output. No other data should be a part of the structured output. The experience_id can be used to match up the experience with the rest of the experience metadata.

    The LLM can chose to make revisions to the provided content to help meet the resume target size.

    The LLM should also be provided the metrics about the lengths of the resume and the previous resume content (experience, skills, professional summary) if set, so it has a reference of the previous contents length as it selects the next iteration of the resume.

    Defer: True

    Reads:
        - user
        - education
        - credentials
        - job_title
        - job_description
        - skills_and_accomplishments
        - experience
        - professional_summary
        - resume_page_target
        - resume (if set)
        - resume_feedback (if set)
        - resume_page_length (if set)
        - word_count (if set)

    Returns:
        - resume: ResumeData # See features/resume/types.py
        - word_count: int
    """
    logger.debug("NODE: resume_generator.select_resume_content")

    # Preconditions
    if state.user is None:
        logger.warning("No user loaded; cannot build resume. Skipping.")
        return PartialInternalState()

    # Prepare inputs for model
    experiences_block = _format_experiences_for_prompt(state)
    education_block = _format_education_for_prompt(state)
    certifications_block = _format_certifications_for_prompt(state)

    previous_resume_text = str(state.resume) if state.resume is not None else ""
    professional_summary_current = state.professional_summary or ""
    resume_feedback = state.resume_feedback or ""
    page_length = state.resume_page_length
    page_target = state.resume_page_target
    prev_word_count = state.word_count

    try:
        result = _chain.invoke(
            {
                "job_title": state.job_title,
                "job_description": state.job_description,
                "professional_summary": professional_summary_current,
                "experiences": experiences_block,
                "education": education_block,
                "certifications": certifications_block,
                "previous_resume": previous_resume_text,
                "resume_feedback": resume_feedback,
                "page_target": f"{page_target:.2f}" if page_target is not None else "",
                "current_page_length": f"{page_length:.2f}" if page_length is not None else "",
                "previous_word_count": str(prev_word_count or ""),
            }
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to select resume content: %s", exc)
        return PartialInternalState()

    structured = _NodeOutput.model_validate(result)

    # Assemble ResumeData
    resume = _assemble_resume_from_selection(state, structured)

    # Compute word count of the content we just assembled
    content_word_count = _estimate_word_count(resume)

    logger.debug(
        "Selected resume content: roles=%d skills=%d words=%d",
        len(resume.experience),
        len(resume.skills),
        content_word_count,
    )

    return PartialInternalState(resume=resume, word_count=content_word_count)


# === Structured output ===
class _SelectedExperience(BaseModel):
    """Experience selection with associated bullet points."""

    experience_id: int = Field(..., description="The id of the experience to include")
    points: list[str] = Field(
        default_factory=list,
        description="Selected resume bullet points for this experience",
    )


class _NodeOutput(BaseModel):
    """LLM-validated selection for the final resume content."""

    professional_summary: str = Field(
        ..., description="Revised professional summary tailored to the job"
    )
    experiences: list[_SelectedExperience] = Field(
        default_factory=list, description="Experiences to include with bullet points"
    )
    selected_skills: list[str] = Field(
        default_factory=list, description="Skills to include in the resume"
    )


# === Prompt ===
_SYSTEM_PROMPT: Final[str] = """
You are an expert resume editor. Your task is to SELECT and lightly EDIT content for a resume to best match the target job while meeting a page-length target.

Rules:
- Only use information provided. Do not invent facts.
- Prefer experiences and bullets that strongly match the job description and demonstrate impact.
- If content is too long, reduce bullets and possibly omit less relevant roles.
- If content is too short, add strong bullets from available accomplishments.
- You MAY revise the professional summary to better align, but keep it concise.
- Return JSON exactly matching the schema with keys: professional_summary, experiences, selected_skills.

Schema:
{{
  "professional_summary": string,
  "experiences": [ {{ "experience_id": number, "points": [string, ...] }}, ... ],
  "selected_skills": [string, ...]
}}
"""

_USER_PROMPT: Final[str] = """
<JobTitle>
{job_title}
</JobTitle>

<JobDescription>
{job_description}
</JobDescription>

<PageConstraints>
TargetPages: {page_target}
CurrentPages: {current_page_length}
PreviousWordCount: {previous_word_count}
</PageConstraints>

<PreviousResume>
{previous_resume}
</PreviousResume>

<Feedback>
{resume_feedback}
</Feedback>

<CurrentProfessionalSummary>
{professional_summary}
</CurrentProfessionalSummary>

<Experiences>
{experiences}
</Experiences>

<Education>
{education}
</Education>

<Certifications>
{certifications}
</Certifications>

Instructions:
- Choose only the most relevant experiences. It is acceptable to exclude roles that do not strengthen alignment.
- For each selected experience, include only the strongest, non-redundant bullet points.
- Deduplicate skills and include a concise list under selected_skills.
"""

_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", _SYSTEM_PROMPT),
        ("user", _USER_PROMPT),
    ]
)
_LLM = get_model(OpenAIModels.gpt_4o_mini).with_structured_output(_NodeOutput)
_CHAIN = _PROMPT | _LLM


# Adapter to keep symbol used in invoke stable for tests/calls.
_chain = _CHAIN


# === Helpers ===
def _format_date(dt: date | None) -> str:
    """Format a date as 'Mon YYYY' or 'Present' for None."""
    if not dt:
        return "Present"
    month_names = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    return f"{month_names[dt.month - 1]} {dt.year}"


def _format_experiences_for_prompt(state: InternalState) -> str:
    """Create a deterministic text block of experiences with extracted content and skills."""
    lines: list[str] = []
    for exp_id, exp in state.experience.items():
        lines.append(f'<Experience id="{exp_id}">')
        lines.append(f"Title: {exp.title}")
        lines.append(f"Company: {exp.company}")
        lines.append(f"Location: {exp.location}")
        lines.append(f"Dates: {_format_date(exp.start_date)} – {_format_date(exp.end_date)}")
        # Include previously extracted accomplishments/skills, if available
        saa = state.skills_and_accomplishments.get(exp_id)
        if saa is not None:
            if saa.accomplishments:
                lines.append("<Accomplishments>")
                for a in saa.accomplishments:
                    lines.append(f"- {a}")
                lines.append("</Accomplishments>")
            if saa.skills:
                lines.append("<Skills>")
                lines.append(", ".join(saa.skills))
                lines.append("</Skills>")
        lines.append("</Experience>\n")
    return "\n".join(lines).strip()


def _format_education_for_prompt(state: InternalState) -> str:
    lines: list[str] = []
    for edu in state.education:
        lines.append("<Edu>")
        lines.append(f"Degree: {edu.degree}")
        lines.append(f"Major: {edu.major}")
        lines.append(f"Institution: {edu.institution}")
        lines.append(f"GradDate: {_format_date(edu.grad_date)}")
        lines.append("</Edu>")
    return "\n".join(lines).strip()


def _format_certifications_for_prompt(state: InternalState) -> str:
    lines: list[str] = []
    for cert in state.credentials:
        lines.append("<Cert>")
        lines.append(f"Title: {cert.title}")
        lines.append(f"Date: {_format_date(cert.date)}")
        lines.append("</Cert>")
    return "\n".join(lines).strip()


def _assemble_resume_from_selection(state: InternalState, sel: _NodeOutput) -> ResumeData:
    """Build ResumeData from selection output and existing state."""
    user = state.user
    assert user is not None

    # Map selected experiences
    experiences: list[ResumeExperience] = []
    for chosen in sel.experiences:
        exp = state.experience.get(chosen.experience_id)
        if exp is None:
            continue
        experiences.append(
            ResumeExperience(
                title=exp.title,
                company=exp.company,
                location=exp.location,
                start_date=_format_date(exp.start_date),
                end_date=_format_date(exp.end_date),
                points=list(chosen.points),
            )
        )

    # Transform education and certifications
    education = [
        ResumeEducation(
            degree=edu.degree,
            major=edu.major,
            institution=edu.institution,
            grad_date=_format_date(edu.grad_date),
        )
        for edu in state.education
    ]
    certifications = [
        ResumeCertification(title=cert.title, date=_format_date(cert.date))
        for cert in state.credentials
    ]

    # Deduplicate skills preserving order
    seen: set[str] = set()
    skills: list[str] = []
    for sk in sel.selected_skills:
        if sk not in seen:
            seen.add(sk)
            skills.append(sk)

    name = getattr(user, "full_name", None) or f"{user.first_name} {user.last_name}".strip()
    email = user.email or ""
    phone = user.phone or ""
    linkedin = user.linkedin_url or ""

    return ResumeData(
        name=name,
        title=state.job_title,
        email=email,
        phone=phone,
        linkedin_url=linkedin,
        professional_summary=sel.professional_summary.strip(),
        experience=experiences,
        education=education,
        skills=skills,
        certifications=certifications,
    )


def _estimate_word_count(resume: ResumeData) -> int:
    """Approximate word count for summary, bullets, and skills."""
    total = 0

    def count_words(text: str) -> int:
        stripped = text.strip()
        if not stripped:
            return 0
        return len([t for t in stripped.replace("\n", " ").split(" ") if t])

    total += count_words(resume.professional_summary)
    for exp in resume.experience:
        for pt in exp.points:
            total += count_words(pt)
    for sk in resume.skills:
        total += count_words(sk)
    return total
