from dataclasses import dataclass

from app.domain.ai.models.chat_message import ChatMessage


@dataclass(slots=True, frozen=True)
class ChatRequest:

    messages: list[ChatMessage]

    stream: bool = True