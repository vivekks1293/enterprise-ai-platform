from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ChatChunk:
    """Represents a streamed response chunk."""

    content: str

    is_final: bool = False