from enum import StrEnum

from langgraph.graph import END, START, StateGraph

from src.core.context import AgentContext

from .nodes import summarize
from .state import InputState, InternalState, OutputState


class Node(StrEnum):
    SUMMARIZE = "summarize"
    START = START
    END = END


builder = StateGraph(
    InternalState,
    input_schema=InputState,
    output_schema=OutputState,
    context_schema=AgentContext,
)

builder.add_node(Node.SUMMARIZE, summarize)

builder.add_edge(Node.START, Node.SUMMARIZE)
builder.add_edge(Node.SUMMARIZE, Node.END)

experience_agent = builder.compile()
