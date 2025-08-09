from __future__ import annotations

from ..state import InternalState, PartialInternalState


def create_professional_summary(state: InternalState) -> PartialInternalState:
    """
    Generate a professional summary for the users resume. This summary should be grounded in the provided experience and responses summary to best align with the job description. This summary should highlight how the user is a unique candidate for the position and should avoid generic statements.

    Defer: True

    Reads:
        - job_description
        - experience_summary
        - responses_summary

    Returns:
        - professional_summary: str
    """
    return PartialInternalState()
