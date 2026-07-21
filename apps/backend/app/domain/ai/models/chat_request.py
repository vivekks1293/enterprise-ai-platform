from dataclasses import dataclass, field

from app.domain.ai.models.chat_message import ChatMessage


@dataclass(slots=True, frozen=True)
class ChatRequest:
    """Represents a chat completion request."""

    messages: list[ChatMessage]

    temperature: float = 0.7

    max_tokens: int | None = None

    stream: bool = True

    metadata: dict[str, str] = field(default_factory=dict)