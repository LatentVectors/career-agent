from langchain.chat_models import init_chat_model
from langgraph.prebuilt import ToolNode

from .state import State
from .tools import TOOLS

llm = init_chat_model("gpt-3.5-turbo")
llm_with_tools = llm.bind_tools(TOOLS)


def chatbot(state: State) -> State:
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


tool_node = ToolNode(tools=TOOLS)
