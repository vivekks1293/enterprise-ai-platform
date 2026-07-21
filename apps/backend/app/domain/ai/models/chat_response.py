from dataclasses import dataclass
from typing import Literal

from app.domain.ai.models.chat_usage import ChatUsage


@dataclass(slots=True, frozen=True)
class ChatResponse:
    """Represents a completed chat response."""

    content: str

    usage: ChatUsage | None = None

    finish_reason: (
        Literal[
            "stop",
            "length",
            "tool_calls",
            "content_filter",
        ]
        | None
    ) = None

    model: str | None = None

    provider: str | None = None