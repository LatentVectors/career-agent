from ..agents import experience_graph
from ..state import MainState, PartialMainState


def summarize_experience_node(state: MainState) -> PartialMainState:
    """Summarize experience."""
    if state["current_experience"] is None or state["current_experience"].content.strip() == "":
        return {"experience_summary": None}

    result = experience_graph.invoke(
        {
            "experience": state["current_experience"].content,
            "job_description": state["job_description"],
        }
    )
    return {"experience_summary": result["summary"]}
