from __future__ import annotations

from ..state import InternalState, PartialInternalState


def extract_skills_and_accomplishments(state: InternalState) -> PartialInternalState:
    """
    Use structured outputs to extract a list of accomplishments and a list of skills from the users experience. The extracted content should be grounded in the users experience and be stated in a way that best matches the language used in the target job description. The accomplishments returned by this node should be stand-alone bullet points for the resume and should follow all the best practices for writing high-quality resume bullet points. A later node will filter through these bullet points to select the best ones. Similarly, the skills will be filtered by the same node to highlight the most relevant content. Return all the skills the user experience demonstrates that are in the job description.

    SkillsAndAccomplishments is a Pydantic model with the following definition:

    SkillsAndAccomplishments
        experience_id: int
        accomplishments: list[str]
        skills: list[str]

    Reads:
        - job_description
        - current_experience_id

    Returns:
        - skills_and_accomplishments: dict[int, SkillsAndAccomplishments] # Reduce using dict update. The Key is the current_experience_id.
    """
    return PartialInternalState()
