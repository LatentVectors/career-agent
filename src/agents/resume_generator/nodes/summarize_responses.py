from __future__ import annotations

from ..state import InternalState, PartialInternalState


def summarize_responses(state: InternalState) -> PartialInternalState:
    """
    Generate a summary of the users candidate responses. The summary will be used to help generate the professional summary and should be grounded in the provided candidate responses and highlight how the candidate aligns with the provided job description. Candidate responses cover a wide range of topics, including strengths, weaknesses, interests, work-style, and other content that is not strictly related to any given position or project. This summary should take advantage of the unique aspect of this data to draw attention to or highlight that those less-tangible ways the user may align well with the target job description.

    Reads:
        - job_description
        - candidate_responses

    Returns:
        - responses_summary: str
    """
    return PartialInternalState()
