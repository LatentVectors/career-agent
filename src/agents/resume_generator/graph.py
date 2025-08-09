from __future__ import annotations

from enum import StrEnum
from typing import Literal

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from src.core.context import AgentContext
from src.logging_config import logger

from .nodes import (
    create_professional_summary,
    extract_skills_and_accomplishments,
    generate_resume_pdf,
    provide_resume_feedback,
    read_db_content,
    select_resume_content,
    summarize_experience,
    summarize_responses,
)
from .state import InputState, InternalState, OutputState


class Node(StrEnum):
    READ_DB_CONTENT = "read_db_content"
    EXTRACT_SKILLS_AND_ACCOMPLISHMENTS = "extract_skills_and_accomplishments"
    SUMMARIZE_EXPERIENCE = "summarize_experience"
    SUMMARIZE_RESPONSES = "summarize_responses"
    CREATE_PROFESSIONAL_SUMMARY = "create_professional_summary"
    SELECT_RESUME_CONTENT = "select_resume_content"
    GENERATE_RESUME_PDF = "generate_resume_pdf"
    PROVIDE_RESUME_FEEDBACK = "provide_resume_feedback"
    START = START
    END = END


builder = StateGraph(
    InternalState, input_schema=InputState, output_schema=OutputState, context_schema=AgentContext
)


# === NODES ===
builder.add_node(Node.READ_DB_CONTENT, read_db_content)
builder.add_node(Node.EXTRACT_SKILLS_AND_ACCOMPLISHMENTS, extract_skills_and_accomplishments)
builder.add_node(Node.SUMMARIZE_EXPERIENCE, summarize_experience)
builder.add_node(Node.SUMMARIZE_RESPONSES, summarize_responses)
builder.add_node(Node.CREATE_PROFESSIONAL_SUMMARY, create_professional_summary, defer=True)
builder.add_node(Node.SELECT_RESUME_CONTENT, select_resume_content, defer=True)
builder.add_node(Node.GENERATE_RESUME_PDF, generate_resume_pdf)
builder.add_node(Node.PROVIDE_RESUME_FEEDBACK, provide_resume_feedback)


# === EDGES ===
def map_experience_edge(state: InternalState) -> list[Send]:
    """Map each experience to both extraction and summarization nodes.

    Reads: experience
    Sets: current_experience_id
    Returns: list[Send]
    """
    logger.debug("EDGE: resume_generator.map_experience_edge")
    next_nodes: list[Send] = []
    if state.experience:
        for exp_id in state.experience.keys():
            # Send a validated internal state per target node
            # TODO: Is this actually returning a new state object?
            # TODO: Add directions on how to implement these edges.
            new_state_extract = InternalState.model_validate(state)
            new_state_extract.current_experience_id = exp_id
            next_nodes.append(Send(Node.EXTRACT_SKILLS_AND_ACCOMPLISHMENTS, new_state_extract))

            new_state_summarize = InternalState.model_validate(state)
            new_state_summarize.current_experience_id = exp_id
            next_nodes.append(Send(Node.SUMMARIZE_EXPERIENCE, new_state_summarize))
    return next_nodes


def route_feedback_edge(
    state: InternalState,
) -> Literal[Node.PROVIDE_RESUME_FEEDBACK, Node.END]:
    """Route based on page length and feedback loop iterations.

    The resume is considered acceptable when
    (resume_page_target - 0.07) <= resume_page_length <= resume_page_target.
    """
    logger.debug("EDGE: resume_generator.route_feedback_edge")
    # Stop looping if iterations exceeded
    if state.feedback_loop_iterations > state.feedback_loop_max_iterations:
        logger.warning(
            "Feedback loop exceeded max iterations: %s > %s",
            state.feedback_loop_iterations,
            state.feedback_loop_max_iterations,
        )
        return Node.END

    page_length = state.resume_page_length
    target = state.resume_page_target
    if page_length is None or target is None:
        return Node.PROVIDE_RESUME_FEEDBACK

    lower_bound = target - 0.07
    meets_target = (page_length >= lower_bound) and (page_length <= target)
    if meets_target:
        return Node.END
    return Node.PROVIDE_RESUME_FEEDBACK


# Linear edges
builder.add_edge(Node.START, Node.READ_DB_CONTENT)
builder.add_conditional_edges(
    Node.READ_DB_CONTENT,
    map_experience_edge,  # type: ignore[arg-type]
    [Node.EXTRACT_SKILLS_AND_ACCOMPLISHMENTS, Node.SUMMARIZE_EXPERIENCE],
)
builder.add_edge(Node.READ_DB_CONTENT, Node.SUMMARIZE_RESPONSES)
builder.add_edge(Node.EXTRACT_SKILLS_AND_ACCOMPLISHMENTS, Node.SELECT_RESUME_CONTENT)
builder.add_edge(Node.SUMMARIZE_RESPONSES, Node.CREATE_PROFESSIONAL_SUMMARY)
builder.add_edge(Node.SUMMARIZE_EXPERIENCE, Node.CREATE_PROFESSIONAL_SUMMARY)
builder.add_edge(Node.CREATE_PROFESSIONAL_SUMMARY, Node.SELECT_RESUME_CONTENT)
builder.add_edge(Node.SELECT_RESUME_CONTENT, Node.GENERATE_RESUME_PDF)
builder.add_conditional_edges(
    Node.GENERATE_RESUME_PDF,
    route_feedback_edge,  # type: ignore[arg-type]
    [Node.PROVIDE_RESUME_FEEDBACK, Node.END],
)
builder.add_edge(Node.PROVIDE_RESUME_FEEDBACK, Node.SELECT_RESUME_CONTENT)


# === GRAPH ===
# TODO: Standardize the names for the compiled graph.
graph = builder.compile()
