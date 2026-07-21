from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ChatResponse:

    content: str