from dataclasses import dataclass
from typing import Literal

from app.domain.ai.models.citation import Citation


@dataclass(slots=True, frozen=True)
class AIStreamEvent:
    """
    Represents an event emitted by the AI runtime
    during a streaming response.
    """

    type: Literal[
        "token",
        "citations",
        "complete",
    ]

    content: str | None = None

    citations: list[Citation] | None = None