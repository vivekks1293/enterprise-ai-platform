from app.application.conversation.dto.list_conversations import (
    ConversationSummary,
    ListConversationsRequest,
    ListConversationsResponse,
)
from app.domain.conversation.repositories.conversation_repository import (
    ConversationRepository,
)


class ListConversationsUseCase:
    """
    Retrieves all conversations belonging to an authenticated user.
    """

    def __init__(
        self,
        conversation_repository: ConversationRepository,
    ) -> None:
        self._conversation_repository = conversation_repository

    async def execute(
        self,
        request: ListConversationsRequest,
    ) -> ListConversationsResponse:
        """
        Returns all conversations owned by the user.
        """

        conversations = await self._conversation_repository.list_by_owner(
            request.owner_id
        )

        summaries = [
            ConversationSummary(
                id=conversation.id,
                title=conversation.title,
                updated_at=conversation.updated_at,
                created_at=conversation.created_at,
            )
            for conversation in conversations
        ]

        return ListConversationsResponse(
            conversations=summaries
        )