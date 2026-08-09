from dataclasses import dataclass, field
from typing import Any

from app.domain.ai.models.chat_message import ChatMessage


@dataclass(slots=True, frozen=True)
class ChatRequest:
    """
    Represents a provider-agnostic chat completion request.
    """

    messages: list[ChatMessage]

    temperature: float = 0.7

    max_tokens: int | None = None

    stream: bool = True

    metadata: dict[str, Any] = field(default_factory=dict)