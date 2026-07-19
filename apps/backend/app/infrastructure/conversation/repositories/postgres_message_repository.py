from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.conversation.entities.message import Message
from app.domain.conversation.repositories.message_repository import (
    MessageRepository,
)
from app.infrastructure.conversation.mappers.message_mapper import (
    to_domain,
    to_model,
)
from app.infrastructure.conversation.models.message_model import (
    MessageModel,
)


class PostgresMessageRepository(MessageRepository):
    """
    PostgreSQL implementation of MessageRepository.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def save(
        self,
        message: Message,
    ) -> None:

        self._session.add(
            to_model(message)
        )

    async def list_by_conversation(
        self,
        conversation_id: UUID,
    ) -> list[Message]:

        result = await self._session.execute(
            select(MessageModel)
            .where(
                MessageModel.conversation_id == conversation_id
            )
            .order_by(
                MessageModel.created_at.asc()
            )
        )

        return [
            to_domain(model)
            for model in result.scalars().all()
        ]