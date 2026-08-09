from collections.abc import AsyncIterator
from datetime import datetime, timezone
from uuid import uuid4

from app.application.ai.orchestrator.ai_orchestrator import (
    AIOrchestrator,
)
from app.application.common.ports.unit_of_work import UnitOfWork
from app.application.conversation.dto.send_prompt import (
    SendPromptRequest,
)
from app.application.conversation.exceptions import (
    ConversationNotFoundError,
)
from app.domain.ai.models.chat_message import ChatMessage
from app.domain.conversation.entities.message import Message
from app.domain.conversation.enums.message_role import (
    MessageRole,
)
from app.domain.conversation.repositories.conversation_repository import (
    ConversationRepository,
)
from app.domain.conversation.repositories.message_repository import (
    MessageRepository,
)


class SendPromptUseCase:
    """
    Handles prompt submission and streams the AI response.
    """

    def __init__(
        self,
        conversation_repository: ConversationRepository,
        message_repository: MessageRepository,
        ai_orchestrator: AIOrchestrator,
        unit_of_work: UnitOfWork,
    ) -> None:

        self._conversation_repository = conversation_repository
        self._message_repository = message_repository
        self._ai_orchestrator = ai_orchestrator
        self._unit_of_work = unit_of_work

    async def execute(
        self,
        request: SendPromptRequest,
    ) -> AsyncIterator[str]:
        """
        Executes the prompt workflow.
        """

        # -----------------------------------------------------
        # Step 1 - Validate conversation ownership
        # -----------------------------------------------------

        conversation = await self._conversation_repository.get_by_id(
            conversation_id=request.conversation_id,
            owner_id=request.owner_id,
        )

        if conversation is None:
            raise ConversationNotFoundError()

        # -----------------------------------------------------
        # Step 2 - Persist user prompt
        # -----------------------------------------------------

        await self._save_user_message(request)

        # -----------------------------------------------------
        # Step 3 - Reload conversation history
        # -----------------------------------------------------

        messages = await self._message_repository.list_by_conversation(
            request.conversation_id,
        )

        # -----------------------------------------------------
        # Step 4 - Convert domain messages to AI messages
        # -----------------------------------------------------

        chat_messages = [
            ChatMessage(
                role=message.role.value,
                content=message.content,
            )
            for message in messages
        ]

        # -----------------------------------------------------
        # Step 5 - Execute AI Runtime
        # -----------------------------------------------------

        response_parts: list[str] = []

        async for token in self._ai_orchestrator.respond(
            conversation_id=request.conversation_id,
            owner_id=request.owner_id,
            messages=chat_messages,
        ):
            response_parts.append(token)

            yield token

        assistant_response = "".join(response_parts)

        # -----------------------------------------------------
        # Step 6 - Persist assistant response
        # -----------------------------------------------------

        await self._save_assistant_message(
            conversation_id=request.conversation_id,
            response=assistant_response,
        )

    async def _save_user_message(
        self,
        request: SendPromptRequest,
    ) -> None:
        """
        Persists the user's prompt.
        """

        message = Message(
            id=uuid4(),
            conversation_id=request.conversation_id,
            role=MessageRole.USER,
            content=request.prompt,
            created_at=datetime.now(timezone.utc),
        )

        await self._message_repository.save(message)

        await self._unit_of_work.commit()

    async def _save_assistant_message(
        self,
        conversation_id,
        response: str,
    ) -> None:
        """
        Persists the assistant response.
        """

        message = Message(
            id=uuid4(),
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=response,
            created_at=datetime.now(timezone.utc),
        )

        await self._message_repository.save(message)

        await self._conversation_repository.touch(
            conversation_id=conversation_id,
            updated_at=datetime.now(timezone.utc),
        )

        await self._unit_of_work.commit()