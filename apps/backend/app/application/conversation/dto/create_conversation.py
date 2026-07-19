from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class CreateConversationRequest:
    """
    Request DTO for creating a conversation.
    """

    owner_id: UUID

    title: str


@dataclass(slots=True)
class CreateConversationResponse:
    """
    Response DTO returned after creating a conversation.
    """

    id: UUID

    title: str

    created_at: datetime

    updated_at: datetime