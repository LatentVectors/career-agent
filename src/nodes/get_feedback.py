from src.hitl import dispatch_message_interrupt
from src.logging_config import logger
from src.state import MainState, PartialMainState


def get_feedback(state: MainState) -> PartialMainState:
    """Get feedback from the user."""
    cover_letter = state["cover_letter"]
    if not cover_letter:
        logger.warning("No cover letter found in state.")
        return {}
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
        return {"cover_letter_feedback": None}
    return {"cover_letter_feedback": content}
