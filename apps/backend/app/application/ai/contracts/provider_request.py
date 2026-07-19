from dataclasses import dataclass, field

from app.application.ai.contracts.chat_message import ChatMessage


@dataclass(slots=True, frozen=True)
class ProviderRequest:
    """
    Request sent from the Application layer to an AI provider.
    """

    messages: list[ChatMessage]

    model: str | None = None

    temperature: float = 0.7

    max_tokens: int | None = None

    metadata: dict[str, str] = field(default_factory=dict)