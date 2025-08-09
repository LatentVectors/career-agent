from __future__ import annotations

from ..state import InternalState, PartialInternalState


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
    return PartialInternalState()
