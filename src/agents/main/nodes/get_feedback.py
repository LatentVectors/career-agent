from src.core.hitl import dispatch_message_interrupt
from src.logging_config import logger

from ..state import InternalState, PartialInternalState


def get_feedback(state: InternalState) -> PartialInternalState:
    """Get feedback from the user."""
    cover_letter = state.cover_letter
    if not cover_letter:
        logger.warning("No cover letter found in state.")
        return PartialInternalState()
    message = (
        "=== COVER LETTER ===\n"
        f"{cover_letter}\n"
        "=== END OF COVER LETTER ===\n"
        "Do you have any feedback for the cover letter?\n"
        "Type your response or type 'no', 'n' or leave your response empty."
    )
    response = dispatch_message_interrupt(message)
    content = response["response"].strip()
    if content.lower() in ["no", "n", ""]:
        return PartialInternalState(cover_letter_feedback=None)
    return PartialInternalState(cover_letter_feedback=content)
