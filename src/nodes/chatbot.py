from src.models import llm_with_tools
from src.state import MainState, PartialMainState


def chatbot(state: MainState) -> PartialMainState:
    """Chatbot node."""
    return {"messages": [llm_with_tools.invoke(state["messages"])]}
