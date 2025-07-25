from src.models import OpenAIModels, get_model
from src.state import MainState, PartialMainState

llm = get_model(OpenAIModels.gpt_3_5_turbo)


def chatbot(state: MainState) -> PartialMainState:
    """Chatbot node."""
    return {"messages": [llm.invoke(state["messages"])]}
