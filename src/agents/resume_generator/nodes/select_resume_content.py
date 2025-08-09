from __future__ import annotations

from datetime import date
from typing import Iterable, Tuple

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


def _tokenize(text: str) -> set[str]:
    tokens: list[str] = []
    current = []
    for ch in text.lower():
        if ch.isalnum():
            current.append(ch)
        else:
            if current:
                tokens.append("".join(current))
                current = []
    if current:
        tokens.append("".join(current))
    # filter very short tokens
    return {t for t in tokens if len(t) > 2}


def _score_point(point: str, job_tokens: set[str]) -> int:
    words = _tokenize(point)
    overlap = len(words & job_tokens)
    # Prefer concise, strong points (medium length)
    length_bonus = 1 if 8 <= len(point.split()) <= 24 else 0
    return overlap * 2 + length_bonus


def _experience_sort_key(
    exp_obj: object,
    exp_id: int,
    job_tokens: set[str],
    saa_skills: list[str],
    current_titles: set[str],
) -> Tuple[int, int, int]:
    # Higher tuple sorts later unless we reverse; we'll reverse in sort
    # Relevance from skills overlap
    skills_overlap = len(_tokenize(" ".join(saa_skills)) & job_tokens)
    # Recency heuristic: end_date None considered most recent
    end_dt: date | None = getattr(exp_obj, "end_date", None)
    start_dt: date | None = getattr(exp_obj, "start_date", None)
    recency_bucket = 2
    if end_dt is None:
        recency_bucket = 3
    elif start_dt and end_dt and (end_dt >= start_dt):
        recency_bucket = 2
    else:
        recency_bucket = 1
    # Continuity bonus if previously selected
    title = getattr(exp_obj, "title", "")
    continuity = 1 if title in current_titles else 0
    return (skills_overlap, recency_bucket, continuity)


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

    Design contract:
        - Build a complete `ResumeData` using DB entities and generated content.
        - Select experiences and bullet points using simple, deterministic heuristics:
          - Rank experiences by skills overlap with job description, recency, and continuity
            with any previously selected resume content.
          - Limit number of experiences and points per experience based on
            `resume_page_target` and adjust with `resume_page_length` and `resume_feedback` when present.
          - Prefer bullet points (accomplishments) that overlap with job description terms
            and have concise length.
        - Aggregate and deduplicate skills across selected experiences; prioritize skills
          appearing in the job description.
        - Include all education and certifications mapped into resume types.
        - Compute and return an overall `word_count` for feedback routing.
        - Do not perform LLM calls here; upstream nodes produce summaries.
    """
    # Assemble top-level identity fields
    user = state.user
    name = user.full_name if user is not None else ""
    email = user.email or "" if user is not None else ""
    phone = user.phone or "" if user is not None else ""
    linkedin_url = user.linkedin_url or "" if user is not None else ""

    title = state.job_title or ""
    professional_summary = state.professional_summary or ""

    # Determine layout constraints from target and previous render
    target = state.resume_page_target or 1.0
    prev_pages = state.resume_page_length
    lower_ok = target - 0.07

    # Base limits by target
    if target < 1.25:
        base_max_exp = 2
        base_points = 3
        max_skills = 12
    elif target < 1.75:
        base_max_exp = 3
        base_points = 4
        max_skills = 15
    else:
        base_max_exp = 4
        base_points = 5
        max_skills = 18

    # Adjust based on previous page length and feedback
    points_adjust = 0
    exp_adjust = 0
    if prev_pages is not None:
        if prev_pages > target:
            # Too long: trim
            over = prev_pages - target
            points_adjust -= 2 if over > 0.25 else 1
            exp_adjust -= 1 if over > 0.4 else 0
        elif prev_pages < lower_ok:
            # Too short: add
            under = lower_ok - prev_pages
            points_adjust += 2 if under > 0.25 else 1
            exp_adjust += 1 if under > 0.3 else 0

    # Use any structured hints in resume_feedback (very simple rules)
    feedback = (state.resume_feedback or "").lower()
    if "fewer bullets" in feedback:
        points_adjust -= 1
    if "more bullets" in feedback:
        points_adjust += 1
    if "fewer roles" in feedback or "fewer experiences" in feedback:
        exp_adjust -= 1
    if "more roles" in feedback or "more experiences" in feedback:
        exp_adjust += 1

    max_exp = max(1, base_max_exp + exp_adjust)
    per_exp_points = max(2, base_points + points_adjust)

    # Prepare scoring context
    job_tokens = _tokenize(state.job_description or "")
    prev_resume = state.resume
    prev_titles: set[str] = set()
    if prev_resume is not None:
        prev_titles = {exp.title for exp in prev_resume.experience}

    # Sort experiences by relevance and recency
    experience_items = list(state.experience.items())

    def sort_tuple(item: tuple[int, object]) -> Tuple[int, int, int]:
        exp_id, exp_obj = item
        saa = state.skills_and_accomplishments.get(exp_id)
        saa_skills = saa.skills if saa else []
        return _experience_sort_key(exp_obj, exp_id, job_tokens, saa_skills, prev_titles)

    experience_items.sort(key=sort_tuple)
    experience_items.reverse()  # highest scores first

    # Pick top-N experiences
    selected_items = experience_items[:max_exp] if max_exp < len(experience_items) else experience_items

    # Build ResumeExperience list and aggregate skills
    experiences: list[ResumeExperience] = []
    aggregated_skills: list[str] = []

    for exp_id, exp in selected_items:
        saa = state.skills_and_accomplishments.get(exp_id)
        all_points: list[str] = []
        if saa and saa.accomplishments:
            all_points = [p.strip() for p in saa.accomplishments if p and p.strip()]
            aggregated_skills.extend([s.strip() for s in saa.skills if s and s.strip()])
        else:
            content: str = getattr(exp, "content", "")
            all_points = _fallback_points_from_content(content)

        # Rank points by overlap with job description
        ranked = sorted(all_points, key=lambda p: _score_point(p, job_tokens), reverse=True)
        points = ranked[:per_exp_points]

        resume_exp = ResumeExperience(
            title=getattr(exp, "title", ""),
            company=getattr(exp, "company", ""),
            location=getattr(exp, "location", ""),
            start_date=_format_month_year(getattr(exp, "start_date", None)),
            end_date=_format_month_year(getattr(exp, "end_date", None)),
            points=points,
        )
        experiences.append(resume_exp)

    # Skills: dedupe, then prioritize those in job description, then cap
    deduped_skills = _dedupe_preserve_order(aggregated_skills)
    in_jd = [s for s in deduped_skills if _tokenize(s) & job_tokens]
    not_in_jd = [s for s in deduped_skills if not (_tokenize(s) & job_tokens)]
    skills = (in_jd + not_in_jd)[:max_skills]

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
