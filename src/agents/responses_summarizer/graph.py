from langgraph.graph import END, START, StateGraph

from .nodes.summarize import summarize
from .state import ResponsesInputState, ResponsesOutputState, ResponsesState

builder = StateGraph(
    input_schema=ResponsesInputState,
    output_schema=ResponsesOutputState,
    state_schema=ResponsesState,
)

SUMMARIZE_NODE = "summarize"


# === NODES ===
builder.add_node(SUMMARIZE_NODE, summarize)


# === EDGES ===
builder.add_edge(START, SUMMARIZE_NODE)
builder.add_edge(SUMMARIZE_NODE, END)

graph = builder.compile()
