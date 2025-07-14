from ..state import PartialState, State
from .models import llm_with_tools


def chatbot(state: State) -> PartialState:
    """Chatbot node."""
    return {"messages": [llm_with_tools.invoke(state["messages"])]}
