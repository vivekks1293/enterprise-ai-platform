from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.conversation.enums.message_role import MessageRole


@dataclass(slots=True)
class Message:
    """
    Domain entity representing a message within a conversation.
    """

    id: UUID

    conversation_id: UUID

    role: MessageRole

    content: str

    created_at: datetime