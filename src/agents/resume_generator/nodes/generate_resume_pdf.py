from __future__ import annotations

from ..state import InternalState, PartialInternalState


def generate_resume_pdf(state: InternalState) -> PartialInternalState:
    """
    Use the ResumeData to generate a PDF for the resume using one of the resume templates. After generating the resume, check its page_length.

    Reads:
        - resume

    Returns:
        - resume_path: Path
        - resume_page_length: float
    """
    return PartialInternalState()
