from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class ListConversationsRequest:
    """
    Request DTO for listing conversations.
    """

    owner_id: UUID


@dataclass(slots=True)
class ConversationSummary:
    id: UUID
    title: str
    updated_at: datetime
    created_at: datetime


@dataclass(slots=True)
class ListConversationsResponse:
    conversations: list[ConversationSummary]