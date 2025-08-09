from __future__ import annotations

from .graph import GRAPH, Node, stream_agent

# Consistent agent handle for discovery and imports
main_agent = GRAPH

__all__ = ["main_agent", "GRAPH", "Node", "stream_agent"]
