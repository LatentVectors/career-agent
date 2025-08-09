from __future__ import annotations

from ..state import InternalState, PartialInternalState


def summarize_experience(state: InternalState) -> PartialInternalState:
    """
    Generate a summary of the experience indicated by the current_experience_id. The summary will be used to help generate the professional summary, and should be grounded the provided experience and highlight how the candidate aligns with the provided job description.

    Reads:
        - job_description
        - current_experience_id

    Returns:
        - experience_summary: dict[int, str] # Reduce with dict update with current_experience_id as the key and the summarized experience as the value.
    """
    return PartialInternalState()
