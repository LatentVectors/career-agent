from typing import Annotated, List, TypedDict, Union

from langgraph.graph.message import BaseMessage, add_messages

from .storage import Job
from .storage.get_background import Background


class ExperienceSummary(TypedDict):
    source: str
    experience: str


class State(TypedDict):
    """State."""

    messages: Annotated[List[BaseMessage], add_messages]
    job: Job
    background: Background
    experience: List[ExperienceSummary]


class PartialState(TypedDict, total=False):
    """Partial state for return types."""

    messages: Annotated[List[BaseMessage], add_messages]
    job: Job
    background: Background
    experience: List[ExperienceSummary]


ReturnState = Union[State, PartialState]
