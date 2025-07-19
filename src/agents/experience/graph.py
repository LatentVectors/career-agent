from langgraph.graph import END, START, StateGraph

from .nodes import review, summarize
from .nodes.job_requirements import get_job_requirements
from .state import ExperienceInputState, ExperienceOutputState, ExperienceState

builder = StateGraph(
    ExperienceState, input_schema=ExperienceInputState, output_schema=ExperienceOutputState
)
SUMMARIZE = "summarize"
REVIEW = "review"
JOB_REQUIREMENTS = "job_requirements"

builder.add_node(SUMMARIZE, summarize)
builder.add_node(REVIEW, review)
builder.add_node(JOB_REQUIREMENTS, get_job_requirements)

builder.add_edge(START, JOB_REQUIREMENTS)
builder.add_edge(START, SUMMARIZE)
builder.add_edge(SUMMARIZE, REVIEW)
builder.add_edge(REVIEW, END)

experience_graph = builder.compile()
