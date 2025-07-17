from langgraph.graph import END, START, StateGraph

from .nodes import review, summarize
from .state import ExperienceInputState, ExperienceOutputState, ExperienceState

builder = StateGraph(
    ExperienceState, input_schema=ExperienceInputState, output_schema=ExperienceOutputState
)
SUMMARIZE = "summarize"
REVIEW = "review"

builder.add_node(SUMMARIZE, summarize)
builder.add_node(REVIEW, review)

builder.add_edge(START, SUMMARIZE)
builder.add_edge(SUMMARIZE, REVIEW)
builder.add_edge(REVIEW, END)

experience_graph = builder.compile()
