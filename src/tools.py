from __future__ import annotations

import random

# Avoid importing heavy classes at runtime when only needed for type
# annotations – guard with TYPE_CHECKING.
from typing import TYPE_CHECKING, Sequence

import typer

# Third-party langchain imports for tooling support
from langchain.tools import tool as llm_tool
from langchain_core.tools import BaseTool

if TYPE_CHECKING:
    pass  # pragma: no cover

app = typer.Typer()


@llm_tool
def get_current_weather() -> str:
    """Return the current weather for the users location."""
    r = random.randint(0, 100)
    if r < 50:
        return "There is fire falling from the sky!"
    return "The weather is sunny and warm."


TOOLS: Sequence[BaseTool] = [get_current_weather]
