from dataclasses import dataclass

from app.domain.conversation.enums.message_role import MessageRole


@dataclass(slots=True, frozen=True)
class ChatMessage:

    role: MessageRole

    content: str