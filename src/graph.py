from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from .nodes.work_experience import summarize_experience
from .state import State

graph_builder = StateGraph(State)

SUMMARIZE_EXPERIENCE_NODE = "summarize_experience"

graph_builder.add_node(SUMMARIZE_EXPERIENCE_NODE, summarize_experience)

graph_builder.add_edge(START, SUMMARIZE_EXPERIENCE_NODE)
graph_builder.add_edge(SUMMARIZE_EXPERIENCE_NODE, END)

memory = MemorySaver()
GRAPH = graph_builder.compile(checkpointer=memory)
