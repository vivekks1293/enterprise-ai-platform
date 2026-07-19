from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class Conversation:
    """
    Domain entity representing a user conversation.

    A conversation owns metadata only.

    Messages are managed independently to avoid
    unnecessarily loading an entire conversation history.
    """

    id: UUID

    owner_id: UUID

    title: str

    created_at: datetime

    updated_at: datetime