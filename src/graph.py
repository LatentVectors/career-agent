from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import tools_condition

from .nodes import chatbot, tool_node
from .state import State

graph_builder = StateGraph(State)

TOOL_NODE = "tools"
CHATBOT_NODE = "chatbot"

graph_builder.add_node(TOOL_NODE, tool_node)
graph_builder.add_node(CHATBOT_NODE, chatbot)

graph_builder.add_edge(START, CHATBOT_NODE)
graph_builder.add_conditional_edges(CHATBOT_NODE, tools_condition)
graph_builder.add_edge(TOOL_NODE, CHATBOT_NODE)
graph_builder.add_edge(CHATBOT_NODE, END)

memory = MemorySaver()
GRAPH = graph_builder.compile(checkpointer=memory)
