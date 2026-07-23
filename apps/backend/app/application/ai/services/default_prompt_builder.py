from app.application.ai.ports.prompt_builder import PromptBuilder
from app.core.config.settings import settings
from app.domain.ai.models.chat_message import ChatMessage
from app.domain.ai.models.chat_request import ChatRequest
from app.domain.ai.models.message_role import MessageRole


class DefaultPromptBuilder(PromptBuilder):

    async def build(
        self,
        *,
        messages: list[ChatMessage],
    ) -> ChatRequest:

        system_message = ChatMessage(
            role=MessageRole.SYSTEM,
            content=settings.ai_system_prompt,
        )

        return ChatRequest(
            messages=[
                system_message,
                *messages,
            ]
        )