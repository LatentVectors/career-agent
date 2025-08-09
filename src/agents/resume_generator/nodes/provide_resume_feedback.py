from __future__ import annotations

from ..state import InternalState, PartialInternalState


def provide_resume_feedback(state: InternalState) -> PartialInternalState:
    """
    Review the current resume and provide feedback for the node that selects content to help it meet the target page-length requirement.

    Reads:
        - resume
        - resume_page_length
        - resume_page_target
        - word_count

    Returns:
        - resume_feedback: str
        - feedback_loop_iterations: int # Reduce to incrementing int.
    """
    return PartialInternalState()
