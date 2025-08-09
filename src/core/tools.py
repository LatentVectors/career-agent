from __future__ import annotations

import random
from typing import Sequence

import typer
from langchain.tools import tool
from langchain_core.tools import BaseTool

app = typer.Typer()


@tool
def get_current_weather() -> str:
    """Return the current weather for the users location."""
    r = random.randint(0, 100)
    if r < 50:
        return "There is fire falling from the sky!"
    return "The weather is sunny and warm."


TOOLS: Sequence[BaseTool] = [get_current_weather]
