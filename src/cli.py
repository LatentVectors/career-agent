from __future__ import annotations

import typer
from langchain.schema import HumanMessage

from .graph import GRAPH
from .logging_config import logger
from .state import State

app = typer.Typer()


@app.command()
def chat() -> None:
    """Chat with the agent."""
    logger.debug("Starting chat")
    print(GRAPH.get_graph().draw_ascii())
    print(f"\n{'=' * 75}\n")

    config = {"configurable": {"thread_id": "1"}}
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        print("\n")
        stream_graph_updates(user_input, config)
        print("\n")


def stream_graph_updates(user_input: str, config: dict) -> None:
    state: State = {"messages": [HumanMessage(content=user_input)]}
    for event in GRAPH.stream(state, config=config):  # type: ignore[arg-type]
        for value in event.values():
            if value is None:
                continue
            print("Assistant:", value["messages"][-1].content)


if __name__ == "__main__":
    app()
