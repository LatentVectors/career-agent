from enum import StrEnum

from langgraph.graph import END, START, StateGraph

from .nodes.summarize import summarize
from .state import InputState, InternalState, OutputState

builder = StateGraph(
    InternalState,
    input_schema=InputState,
    output_schema=OutputState,
)


class Node(StrEnum):
    SUMMARIZE = "summarize"
    START = START
    END = END


# === NODES ===
builder.add_node(Node.SUMMARIZE, summarize)


# === EDGES ===
builder.add_edge(Node.START, Node.SUMMARIZE)
builder.add_edge(Node.SUMMARIZE, Node.END)

graph = builder.compile()
