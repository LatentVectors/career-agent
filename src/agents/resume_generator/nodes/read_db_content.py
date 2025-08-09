from __future__ import annotations

from ..state import InternalState, PartialInternalState


def read_db_content(state: InternalState) -> PartialInternalState:
    """
    Read user information from the database using the db_manager. Get the user_id from the context. The invoking parent is responsible for passing in the context to the graph.

    Reads:
        - context.user_id # From Context API

    Returns:
        - user: User # From db/models
        - education: list[Education] # From db/models
        - credentials: list[Certification] # From db/models
        - experience: dict[int, Experience] # From db/models. The dict key is the experience ID.
        - candidate_responses: list[CandidateResponse] # From db/models
    """
    return PartialInternalState()
