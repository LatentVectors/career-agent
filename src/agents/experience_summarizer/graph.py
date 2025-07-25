from langgraph.graph import END, START, StateGraph

from .nodes import summarize
from .state import ExperienceInputState, ExperienceOutputState, ExperienceState

builder = StateGraph(
    ExperienceState, input_schema=ExperienceInputState, output_schema=ExperienceOutputState
)
SUMMARIZE = "summarize"
JOB_REQUIREMENTS = "job_requirements"

builder.add_node(SUMMARIZE, summarize)

builder.add_edge(START, SUMMARIZE)
builder.add_edge(SUMMARIZE, END)

experience_graph = builder.compile()
