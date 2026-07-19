from datetime import datetime, timezone
from uuid import uuid4

from app.application.common.ports.unit_of_work import UnitOfWork
from app.application.conversation.dto.create_conversation import (
    CreateConversationRequest,
    CreateConversationResponse,
)
from app.domain.conversation.entities.conversation import Conversation
from app.domain.conversation.repositories.conversation_repository import (
    ConversationRepository,
)


class CreateConversationUseCase:
    """
    Creates a new conversation for the authenticated user.
    """

    def __init__(
        self,
        conversation_repository: ConversationRepository,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._conversation_repository = conversation_repository
        self._unit_of_work = unit_of_work

    async def execute(
        self,
        request: CreateConversationRequest,
    ) -> CreateConversationResponse:
        """
        Creates and persists a new conversation.
        """

        now = datetime.now(timezone.utc)

        conversation = Conversation(
            id=uuid4(),
            owner_id=request.owner_id,
            title=request.title,
            created_at=now,
            updated_at=now,
        )

        try:
            await self._conversation_repository.create(
                conversation
            )

            await self._unit_of_work.commit()

        except Exception:
            await self._unit_of_work.rollback()
            raise

        return CreateConversationResponse(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
        )
    
    #"id": "362d210e-d2df-405b-9e2e-7236f325f769",