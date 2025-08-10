from __future__ import annotations

from .graph import graph
from .state import InputState, OutputState

main_agent = graph

__all__ = ["main_agent", "InputState", "OutputState"]
