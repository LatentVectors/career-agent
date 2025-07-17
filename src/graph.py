from typing import List

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from .nodes import summarize_experience_node
from .state import MainState

# === NODES ===
SUMMARIZE_EXPERIENCE_NODE = "summarize_experience"

builder = StateGraph(MainState)
builder.add_node(SUMMARIZE_EXPERIENCE_NODE, summarize_experience_node)


# === EDGES ===
def summarize_experience_edge(state: MainState) -> List[Send]:
    """Summarize experience edge."""
    next_nodes: List[Send] = []
    if len(state["experience"]) > 0:
        for exp in state["experience"]:
            next_nodes.append(
                Send(
                    SUMMARIZE_EXPERIENCE_NODE,
                    {"current_experience": exp, "job_description": state["job_description"]},
                )
            )
    return next_nodes


builder.add_conditional_edges(START, summarize_experience_edge)  # type: ignore[arg-type]
builder.add_edge(SUMMARIZE_EXPERIENCE_NODE, END)


# === GRAPH ===
memory = MemorySaver()
GRAPH = builder.compile(checkpointer=memory)
