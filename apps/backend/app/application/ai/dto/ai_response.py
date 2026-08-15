from dataclasses import dataclass

from app.domain.ai.models.citation import Citation


@dataclass(slots=True, frozen=True)
class AIResponse:
    """
    Represents the completed AI response together with
    its supporting source citations.
    """

    content: str

    citations: list[Citation]