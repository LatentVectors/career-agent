from langchain.chat_models import init_chat_model
from openai import APIConnectionError

from .tools import TOOLS

llm = init_chat_model("gpt-3.5-turbo")
llm_with_retry = llm.with_retry(retry_if_exception_type=(APIConnectionError,))
llm_with_tools = llm.bind_tools(TOOLS).with_retry(retry_if_exception_type=(APIConnectionError,))
