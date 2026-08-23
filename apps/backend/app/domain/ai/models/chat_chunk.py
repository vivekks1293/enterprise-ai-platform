from dataclasses import dataclass

from app.domain.ai.models.chat_usage import ChatUsage


@dataclass(slots=True, frozen=True)
class ChatChunk:
    """Represents a streamed response chunk."""

    content: str

    is_final: bool = False

    usage: ChatUsage | None = None