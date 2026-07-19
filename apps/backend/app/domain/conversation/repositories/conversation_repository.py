from abc import ABC, abstractmethod
from uuid import UUID
from datetime import datetime
from app.domain.conversation.entities.conversation import Conversation


class ConversationRepository(ABC):
    """
    Repository contract for managing conversations.
    """

    @abstractmethod
    async def create(
        self,
        conversation: Conversation,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(
        self,
        conversation_id: UUID,
        owner_id: UUID,
    ) -> Conversation | None:
        raise NotImplementedError

    @abstractmethod
    async def list_by_owner(
        self,
        owner_id: UUID,
    ) -> list[Conversation]:
        raise NotImplementedError

    @abstractmethod
    async def delete(
        self,
        conversation_id: UUID,
        owner_id: UUID,
    ) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def touch(
        self,
        conversation_id: UUID,
        updated_at: datetime,
    ) -> None:
        """
        Updates the conversation's last modified timestamp.
        """
        raise NotImplementedError