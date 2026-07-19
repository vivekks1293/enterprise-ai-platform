from uuid import UUID
from datetime import datetime

from sqlalchemy import update
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.conversation.entities.conversation import Conversation
from app.domain.conversation.repositories.conversation_repository import (
    ConversationRepository,
)
from app.infrastructure.conversation.mappers.conversation_mapper import (
    to_domain,
    to_model,
)
from app.infrastructure.conversation.models.conversation_model import (
    ConversationModel,
)


class PostgresConversationRepository(ConversationRepository):
    """
    PostgreSQL implementation of ConversationRepository.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def create(
        self,
        conversation: Conversation,
    ) -> None:

        self._session.add(
            to_model(conversation)
        )

    async def get_by_id(
        self,
        conversation_id: UUID,
        owner_id: UUID,
    ) -> Conversation | None:

        result = await self._session.execute(
                    select(ConversationModel).where(
                ConversationModel.id == conversation_id,
                ConversationModel.owner_id == owner_id,
            )
        )

        model = result.scalar_one_or_none()

        if model is None:
            return None

        return to_domain(model)

    async def list_by_owner(
        self,
        owner_id: UUID,
    ) -> list[Conversation]:

        result = await self._session.execute(
            select(ConversationModel)
            .where(
                ConversationModel.owner_id == owner_id
            )
            .order_by(
                ConversationModel.updated_at.desc()
            )
        )

        return [
            to_domain(model)
            for model in result.scalars().all()
        ]

    async def delete(
        self,
        conversation_id: UUID,
        owner_id: UUID,
    ) -> None:

        result = await self._session.execute(
                        select(ConversationModel).where(
                ConversationModel.id == conversation_id,
                ConversationModel.owner_id == owner_id,
            )
        )

        model = result.scalar_one_or_none()

        if model is not None:
            await self._session.delete(model)

    async def touch(
    self,
    conversation_id: UUID,
    updated_at: datetime,
    ) -> None:

        stmt = (
            update(ConversationModel)
            .where(
                ConversationModel.id == conversation_id
            )
            .values(
                updated_at=updated_at
            )
        )

        await self._session.execute(stmt)