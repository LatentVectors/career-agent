from __future__ import annotations

from enum import StrEnum
from typing import List, Literal

from langchain_core.runnables.config import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command, Send

from src.hitl import INTERRUPT_KEY, handle_interrupts

from .logging_config import logger
from .nodes import (
    get_feedback,
    get_job_requirements,
    wrapped_experience_agent,
    wrapped_responses_agent,
    write_cover_letter,
)
from .state import MainInputState, MainState


# === NODES ===
class Node(StrEnum):
    WRAPPED_EXPERIENCE_AGENT = "wrapped_experience_agent"
    GET_JOB_REQUIREMENTS = "get_job_requirements"
    WRITE_COVER_LETTER = "write_cover_letter"
    WRAPPED_RESPONSES_AGENT = "wrapped_responses_agent"
    FEEDBACK = "get_feedback"
    END = END
    START = START


builder = StateGraph(MainState)
builder.add_node(Node.WRAPPED_EXPERIENCE_AGENT, wrapped_experience_agent)
builder.add_node(Node.GET_JOB_REQUIREMENTS, get_job_requirements)
builder.add_node(Node.WRITE_COVER_LETTER, write_cover_letter, defer=True)
builder.add_node(Node.WRAPPED_RESPONSES_AGENT, wrapped_responses_agent)
builder.add_node(Node.FEEDBACK, get_feedback)


# === EDGES ===
def map_experience_edge(state: MainState) -> List[Send]:
    """Map experience edge."""
    next_nodes: List[Send] = []
    if len(state["experience"]) > 0:
        for exp in state["experience"]:
            next_nodes.append(
                Send(
                    Node.WRAPPED_EXPERIENCE_AGENT,
                    {
                        "current_experience": exp.content,
                        "current_experience_title": exp.title,
                        "job_requirements": state["job_requirements"],
                    },
                )
            )
    return next_nodes


def route_cover_letter_feedback_edge(
    state: MainState,
) -> Literal[Node.WRITE_COVER_LETTER, Node.END]:
    """Route cover letter feedback edge."""
    cover_letter_feedback = state["cover_letter_feedback"]
    if cover_letter_feedback:
        return Node.WRITE_COVER_LETTER
    return Node.END


builder.add_edge(Node.START, Node.GET_JOB_REQUIREMENTS)
builder.add_conditional_edges(
    Node.GET_JOB_REQUIREMENTS,
    map_experience_edge,  # type: ignore[arg-type]
    [Node.WRAPPED_EXPERIENCE_AGENT],
)
builder.add_edge(Node.GET_JOB_REQUIREMENTS, Node.WRAPPED_RESPONSES_AGENT)
builder.add_edge(Node.WRAPPED_EXPERIENCE_AGENT, Node.WRITE_COVER_LETTER)
builder.add_edge(Node.WRAPPED_RESPONSES_AGENT, Node.WRITE_COVER_LETTER)
builder.add_edge(Node.WRITE_COVER_LETTER, Node.FEEDBACK)
builder.add_conditional_edges(
    Node.FEEDBACK,
    route_cover_letter_feedback_edge,
    [Node.WRITE_COVER_LETTER, Node.END],
)


# === GRAPH ===
memory = MemorySaver()
GRAPH = builder.compile(checkpointer=memory)


def stream_agent(
    input_state: MainInputState, config: RunnableConfig
) -> CompiledStateGraph[MainState, None, MainState, MainState]:
    """Stream the agent.

    Args:
        input_state: The input state.
        thread_id: The thread ID.

    Returns:
        The compiled state graph.
    """

    logger.info("Starting agent...")
    current_input: object = input_state
    while True:
        stream = GRAPH.stream(current_input, config=config)  # type: ignore[arg-type]
        interrupted: bool = False
        for event in stream:
            logger.info("--> Event Batch <--")
            for key in event.keys():
                logger.info(f"EVENT: {key}")
            interrupts = event.get(INTERRUPT_KEY, None)
            if interrupts:
                logger.info("Interrupts:")
                commands = handle_interrupts(interrupts)
                current_input = Command(resume=commands)
                interrupted = True
                break
        if not interrupted:
            break
    return GRAPH  # type: ignore[return-value]
