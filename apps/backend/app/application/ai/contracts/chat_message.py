from dataclasses import dataclass

from app.domain.conversation.enums.message_role import MessageRole


@dataclass(slots=True, frozen=True)
class ChatMessage:
    """
    Represents a message exchanged with an AI provider.

    This is an application-level contract and is intentionally
    independent of the Conversation domain entity.
    """

    role: MessageRole

    content: str