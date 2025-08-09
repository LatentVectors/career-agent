from __future__ import annotations

from datetime import date
from typing import Iterable

from src.features.resume.types import (
    ResumeCertification,
    ResumeData,
    ResumeEducation,
    ResumeExperience,
)

from ..state import InternalState, PartialInternalState


def _format_month_year(value: date | None) -> str:
    if value is None:
        return "Present"
    # Example: Jan 2024
    try:
        return value.strftime("%b %Y")
    except Exception:
        return str(value)


def _count_words(parts: Iterable[str]) -> int:
    count = 0
    for part in parts:
        if not part:
            continue
        count += len(part.split())
    return count


def _dedupe_preserve_order(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        key = item.strip()
        if not key:
            continue
        if key.lower() in seen:
            continue
        seen.add(key.lower())
        result.append(key)
    return result


def _fallback_points_from_content(content: str) -> list[str]:
    # Basic fallback: split on newlines and bullets, strip empties
    raw_lines = [line.strip(" •-\t") for line in content.splitlines()]
    return [line for line in raw_lines if line]


def select_resume_content(state: InternalState) -> PartialInternalState:
    """
    Review the generated resume content and select the most compelling experience, skills, and accomplishments to include in the final resume. If provided take into account the feedback, previous content, page length, and word count to refine the resume to meet the target page count. Beyond filtering experience, minor editing of accomplishments and refinement of the professional summary may also be used to generate the strongest possible resume for the target job description.

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
    # Assemble top-level identity fields
    user = state.user
    name = user.full_name if user is not None else ""
    email = user.email or "" if user is not None else ""
    phone = user.phone or "" if user is not None else ""
    linkedin_url = user.linkedin_url or "" if user is not None else ""

    title = state.job_title or ""
    professional_summary = state.professional_summary or ""

    # Collect experiences sorted by most recent (end_date None -> Present, sort first)
    experiences: list[ResumeExperience] = []
    # Sort keys deterministically
    experience_items = list(state.experience.items())

    def sort_key(item: tuple[int, object]) -> tuple[int, date | None, date | None]:
        exp = item[1]
        # type: ignore[attr-defined]
        end_dt: date | None = getattr(exp, "end_date", None)
        start_dt: date | None = getattr(exp, "start_date", None)
        # None end_date means current; sort it before others by using max date indicator
        # We will sort descending by end_date then descending by start_date, so invert later
        return (0 if end_dt is None else 1, end_dt, start_dt)

    # Sort so that current (None end_date) come first, then later end dates; reverse to have newest first
    experience_items.sort(key=sort_key)
    experience_items.reverse()

    # Gather skills across experiences for overall skills list
    aggregated_skills: list[str] = []

    for exp_id, exp in experience_items:
        # Pull accomplishments from skills_and_accomplishments if available
        saa = state.skills_and_accomplishments.get(exp_id)
        points: list[str] = []
        if saa and saa.accomplishments:
            points = [p.strip() for p in saa.accomplishments if p and p.strip()]
            # Aggregate skills for top-level section
            aggregated_skills.extend([s.strip() for s in saa.skills if s and s.strip()])
        else:
            # Fallback to parsing Experience.content
            content: str = getattr(exp, "content", "")
            points = _fallback_points_from_content(content)

        resume_exp = ResumeExperience(
            title=getattr(exp, "title", ""),
            company=getattr(exp, "company", ""),
            location=getattr(exp, "location", ""),
            start_date=_format_month_year(getattr(exp, "start_date", None)),
            end_date=_format_month_year(getattr(exp, "end_date", None)),
            points=points,
        )
        experiences.append(resume_exp)

    # Deduplicate and lightly prioritize skills (by first occurrence)
    skills = _dedupe_preserve_order(aggregated_skills)

    # Education mapping
    education: list[ResumeEducation] = []
    for edu in state.education:
        education.append(
            ResumeEducation(
                degree=getattr(edu, "degree", ""),
                major=getattr(edu, "major", ""),
                institution=getattr(edu, "institution", ""),
                grad_date=_format_month_year(getattr(edu, "grad_date", None)),
            )
        )

    # Certifications mapping
    certifications: list[ResumeCertification] = []
    for cert in state.credentials:
        certifications.append(
            ResumeCertification(
                title=getattr(cert, "title", ""),
                date=_format_month_year(getattr(cert, "date", None)),
            )
        )

    resume = ResumeData(
        name=name,
        title=title,
        email=email,
        phone=phone,
        linkedin_url=linkedin_url,
        professional_summary=professional_summary,
        experience=experiences,
        education=education,
        skills=skills,
        certifications=certifications,
    )

    # Compute a simple word count for downstream feedback routing
    word_sources: list[str] = [
        resume.name,
        resume.title,
        resume.email,
        resume.phone,
        resume.linkedin_url,
        resume.professional_summary,
    ]
    for e in resume.experience:
        word_sources.extend([e.title, e.company, e.location, e.start_date, e.end_date])
        word_sources.extend(e.points)
    for edu in resume.education:
        word_sources.extend([edu.degree, edu.major, edu.institution, edu.grad_date])
    word_sources.extend(resume.skills)
    for cert in resume.certifications:
        word_sources.extend([cert.title, cert.date])

    word_count = _count_words(word_sources)

    return PartialInternalState(resume=resume, word_count=word_count)
