from enum import StrEnum

from langgraph.graph import END, START, StateGraph

from src.context import AgentContext

from .nodes import (
    assemble_resume,
    extract_skills,
    fetch_user_data,
    generate_experience_bullets,
    generate_pdf,
    generate_professional_summary,
    optimize_content,
)
from .state import InputState, InternalState, OutputState


class Node(StrEnum):
    """Nodes in the resume generator graph."""

    FETCH_USER_DATA = "fetch_user_data"
    EXTRACT_SKILLS = "extract_skills"
    GENERATE_EXPERIENCE_BULLETS = "generate_experience_bullets"
    GENERATE_PROFESSIONAL_SUMMARY = "generate_professional_summary"
    ASSEMBLE_RESUME = "assemble_resume"
    GENERATE_PDF = "generate_pdf"
    OPTIMIZE_CONTENT = "optimize_content"
    START = START
    END = END


def should_optimize(state: InternalState) -> str:
    """Determine if content optimization is needed.

    Args:
        state: Current state

    Returns:
        Next node name
    """
    if state.page_length > 1 and state.optimization_attempts < 4:
        return Node.OPTIMIZE_CONTENT
    return Node.END


def should_continue_optimization(state: InternalState) -> str:
    """Determine if optimization should continue.

    Args:
        state: Current state

    Returns:
        Next node name
    """
    if state.page_length > 1 and state.optimization_attempts < 4:
        return Node.ASSEMBLE_RESUME
    return Node.END


builder = StateGraph(
    InternalState,
    input_schema=InputState,
    output_schema=OutputState,
    context_schema=AgentContext,
)

# Add nodes
builder.add_node(Node.FETCH_USER_DATA, fetch_user_data)
builder.add_node(Node.EXTRACT_SKILLS, extract_skills)
builder.add_node(Node.GENERATE_EXPERIENCE_BULLETS, generate_experience_bullets)
builder.add_node(Node.GENERATE_PROFESSIONAL_SUMMARY, generate_professional_summary)
builder.add_node(Node.ASSEMBLE_RESUME, assemble_resume)
builder.add_node(Node.GENERATE_PDF, generate_pdf)
builder.add_node(Node.OPTIMIZE_CONTENT, optimize_content)

# Add edges
builder.add_edge(Node.START, Node.FETCH_USER_DATA)
builder.add_edge(Node.FETCH_USER_DATA, Node.EXTRACT_SKILLS)
builder.add_edge(Node.EXTRACT_SKILLS, Node.GENERATE_EXPERIENCE_BULLETS)
builder.add_edge(Node.GENERATE_EXPERIENCE_BULLETS, Node.GENERATE_PROFESSIONAL_SUMMARY)
builder.add_edge(Node.GENERATE_PROFESSIONAL_SUMMARY, Node.ASSEMBLE_RESUME)
builder.add_edge(Node.ASSEMBLE_RESUME, Node.GENERATE_PDF)
builder.add_conditional_edges(
    Node.GENERATE_PDF,
    should_optimize,
    {
        Node.OPTIMIZE_CONTENT: Node.OPTIMIZE_CONTENT,
        Node.END: Node.END,
    },
)
builder.add_conditional_edges(
    Node.OPTIMIZE_CONTENT,
    should_continue_optimization,
    {
        Node.ASSEMBLE_RESUME: Node.ASSEMBLE_RESUME,
        Node.END: Node.END,
    },
)

resume_agent = builder.compile()
