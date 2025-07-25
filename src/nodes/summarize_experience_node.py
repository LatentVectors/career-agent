from ..agents.experience_summarizer import (
    ExperienceInputState,
    ExperienceOutputState,
    experience_graph,
)
from ..state import MainState, PartialMainState


def summarize_experience_node(state: MainState) -> PartialMainState:
    """Summarize experience."""
    title = state["current_experience_title"]
    if title is None:
        raise ValueError("Current experience title is required")
    experience = state["current_experience"]
    if experience is None or experience.strip() == "":
        raise ValueError("Current experience is required")
    job_requirements = state["job_requirements"]
    if job_requirements is None:
        raise ValueError("Job requirements are required")
    input_state: ExperienceInputState = {
        "experience": experience,
        "job_requirements": job_requirements,
    }
    result: ExperienceOutputState = experience_graph.invoke(input_state)  # type: ignore
    summaries = result["summary"]
    if summaries is None:
        return {"summarized_experience": {title: []}}
    return {
        "summarized_experience": {
            title: [
                {
                    "requirements": summary["requirement"],
                    "summary": summary["summary"],
                }
                for summary in summaries
            ]
        }
    }
