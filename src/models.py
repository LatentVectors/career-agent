from enum import Enum
from typing import Dict

from langchain.chat_models import init_chat_model
from langchain.chat_models.base import BaseChatModel


class OpenAIModels(Enum):
    gpt_4o_mini = "openai:gpt-4o-mini"
    """GPT-4o Mini"""
    gpt_4o = "openai:gpt-4o"
    """GPT-4o"""
    gpt_3_5_turbo = "openai:gpt-3.5-turbo"
    """GPT-3.5 Turbo"""


ModelName = OpenAIModels

_models: Dict[ModelName, BaseChatModel] = {}


def get_model(model: ModelName, max_retries: int = 2) -> BaseChatModel:
    """Get a model by name.

    Args:
        model_name: The name of the model.
        **kwargs: Additional keyword arguments to pass to the model.

    Returns:
        A singleton instance of the model.
    """
    if model not in _models:
        _models[model] = init_chat_model(model.value, max_retries=max_retries)
    return _models[model]
