import json
from typing import Any, Union

from pydantic import BaseModel


class PydanticEncoder(json.JSONEncoder):
    """
    A custom JSON encoder to handle Pydantic models.
    """

    def default(self, obj: Any) -> Any:
        if isinstance(obj, BaseModel):
            return obj.model_dump(mode="json")
        return super().default(obj)


def serialize_state(state: Union[dict, BaseModel], indent: int = 4) -> str:
    """
    Serializes a LangGraph state object, potentially containing Pydantic models, into a JSON string.

    Args:
        state: The LangGraph state object (as a dictionary).

    Returns:
        A JSON formatted string representing the state.
    """
    return json.dumps(state, indent=indent, cls=PydanticEncoder)
