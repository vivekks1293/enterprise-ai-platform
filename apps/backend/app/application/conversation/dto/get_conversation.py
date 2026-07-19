from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.conversation.enums.message_role import MessageRole


@dataclass(slots=True)
class GetConversationRequest:
    """
    Request DTO for retrieving a conversation.
    """

    conversation_id: UUID

    owner_id: UUID


@dataclass(slots=True)
class MessageItem:
    """
    Message returned as part of a conversation.
    """

    id: UUID

    role: MessageRole

    content: str

    created_at: datetime


@dataclass(slots=True)
class GetConversationResponse:
    """
    Full conversation including messages.
    """

    id: UUID

    title: str

    created_at: datetime

    updated_at: datetime

    messages: list[MessageItem]