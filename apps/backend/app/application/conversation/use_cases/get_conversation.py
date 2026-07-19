from app.application.conversation.dto.get_conversation import (
    GetConversationRequest,
    GetConversationResponse,
    MessageItem,
)
from app.domain.conversation.repositories.conversation_repository import (
    ConversationRepository,
)
from app.domain.conversation.repositories.message_repository import (
    MessageRepository,
)


class GetConversationUseCase:
    """
    Retrieves a conversation together with its messages.
    """

    def __init__(
        self,
        conversation_repository: ConversationRepository,
        message_repository: MessageRepository,
    ) -> None:
        self._conversation_repository = conversation_repository
        self._message_repository = message_repository

    async def execute(
        self,
        request: GetConversationRequest,
    ) -> GetConversationResponse:

        conversation = await self._conversation_repository.get_by_id(
            conversation_id=request.conversation_id,
            owner_id=request.owner_id,
        )

        if conversation is None:
            raise ValueError("Conversation not found.")

        messages = await self._message_repository.list_by_conversation(
            request.conversation_id
        )

        return GetConversationResponse(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            messages=[
                MessageItem(
                    id=message.id,
                    role=message.role,
                    content=message.content,
                    created_at=message.created_at,
                )
                for message in messages
            ],
        )