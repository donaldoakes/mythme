from typing import Literal
from dataclasses import dataclass

MessageRole = Literal["user", "assistant", "system"]


@dataclass
class ChatMessage:
    role: MessageRole
    content: str


@dataclass
class ChatContent:
    type: Literal["text"]
    text: str


@dataclass
class ChatResponse:
    id: str
    model: str
    type: Literal["message"]
    role: MessageRole
    content: ChatContent
    # TODO: tokens
