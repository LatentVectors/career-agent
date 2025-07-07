from typing import Annotated, List, TypedDict

from langgraph.graph.message import BaseMessage, add_messages


class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
