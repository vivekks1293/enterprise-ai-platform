from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies.database import get_db_session

from app.domain.conversation.repositories.conversation_repository import (
    ConversationRepository,
)
from app.domain.conversation.repositories.message_repository import (
    MessageRepository,
)

from app.infrastructure.conversation.repositories.postgres_conversation_repository import (
    PostgresConversationRepository,
)
from app.infrastructure.conversation.repositories.postgres_message_repository import (
    PostgresMessageRepository,
)


def get_conversation_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ConversationRepository:
    """
    Provides the PostgreSQL implementation of ConversationRepository.
    """
    return PostgresConversationRepository(session=session)


def get_message_repository(
    session: AsyncSession = Depends(get_db_session),
) -> MessageRepository:
    """
    Provides the PostgreSQL implementation of MessageRepository.
    """
    return PostgresMessageRepository(session=session)