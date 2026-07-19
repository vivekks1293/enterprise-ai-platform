from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.conversation.entities.message import Message


class MessageRepository(ABC):
    """
    Repository contract for managing conversation messages.
    """

    @abstractmethod
    async def save(
        self,
        message: Message,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def list_by_conversation(
        self,
        conversation_id: UUID,
    ) -> list[Message]:
        raise NotImplementedError