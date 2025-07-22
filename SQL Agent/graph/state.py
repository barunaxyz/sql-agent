from typing import TypedDict, Optional
from langchain_core.messages import BaseMessage

class ChatState(TypedDict):
    messages: list[BaseMessage]
    user_input: Optional[str]
    answer: Optional[str]