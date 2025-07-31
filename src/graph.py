from typing import List

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from .nodes import (
    get_job_requirements,
    wrapped_experience_agent,
    wrapped_responses_agent,
    write_cover_letter,
)
from .state import MainState

# === NODES ===
WRAPPED_EXPERIENCE_AGENT_NODE = "wrapped_experience_agent"
GET_JOB_REQUIREMENTS_NODE = "get_job_requirements"
WRITE_COVER_LETTER_NODE = "write_cover_letter"
WRAPPED_RESPONSES_AGENT_NODE = "wrapped_responses_agent"

builder = StateGraph(MainState)
builder.add_node(WRAPPED_EXPERIENCE_AGENT_NODE, wrapped_experience_agent)
builder.add_node(GET_JOB_REQUIREMENTS_NODE, get_job_requirements)
builder.add_node(WRITE_COVER_LETTER_NODE, write_cover_letter, defer=True)
builder.add_node(WRAPPED_RESPONSES_AGENT_NODE, wrapped_responses_agent)


# === EDGES ===
def summarize_experience_edge(state: MainState) -> List[Send]:
    """Summarize experience edge."""
    next_nodes: List[Send] = []
    if len(state["experience"]) > 0:
        for exp in state["experience"]:
            next_nodes.append(
                Send(
                    WRAPPED_EXPERIENCE_AGENT_NODE,
                    {
                        "current_experience": exp.content,
                        "current_experience_title": exp.title,
                        "job_requirements": state["job_requirements"],
                    },
                )
            )
    return next_nodes


builder.add_edge(START, GET_JOB_REQUIREMENTS_NODE)
builder.add_conditional_edges(GET_JOB_REQUIREMENTS_NODE, summarize_experience_edge)  # type: ignore[arg-type]
builder.add_edge(GET_JOB_REQUIREMENTS_NODE, WRAPPED_RESPONSES_AGENT_NODE)
builder.add_edge(WRAPPED_EXPERIENCE_AGENT_NODE, WRITE_COVER_LETTER_NODE)
builder.add_edge(WRAPPED_RESPONSES_AGENT_NODE, WRITE_COVER_LETTER_NODE)
builder.add_edge(WRITE_COVER_LETTER_NODE, END)


# === GRAPH ===
memory = MemorySaver()
GRAPH = builder.compile(checkpointer=memory)
