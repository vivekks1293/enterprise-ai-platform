from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ChatChunk:

    content: str