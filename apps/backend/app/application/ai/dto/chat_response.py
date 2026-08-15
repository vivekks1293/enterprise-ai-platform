from dataclasses import dataclass

from app.application.ai.contracts.citation import Citation


@dataclass(slots=True)
class ChatResponse:
    """
    Represents the completed AI response returned
    after streaming has finished.
    """

    content: str

    citations: list[Citation]