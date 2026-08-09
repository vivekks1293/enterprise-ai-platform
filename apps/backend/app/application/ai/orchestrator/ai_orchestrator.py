from collections.abc import AsyncIterator
from uuid import UUID

from app.application.ai.dto.prompt_context import PromptContext
from app.application.ai.ports.chat_provider_resolver import (
    ChatProviderResolver,
)
from app.application.ai.ports.prompt_builder import (
    PromptBuilder,
)
from app.application.ai.retrieval.document_retrieval_service import (
    DocumentRetrievalService,
)
from app.domain.ai.models.chat_message import ChatMessage


class AIOrchestrator:
    """
    Coordinates the Enterprise AI execution pipeline.

    Pipeline
    --------
    1. Retrieve knowledge
    2. Build prompt
    3. Resolve provider
    4. Stream response
    """

    def __init__(
        self,
        retrieval_service: DocumentRetrievalService,
        prompt_builder: PromptBuilder,
        chat_provider_resolver: ChatProviderResolver,
    ) -> None:

        self._retrieval_service = retrieval_service
        self._prompt_builder = prompt_builder
        self._chat_provider_resolver = chat_provider_resolver

    async def respond(
        self,
        *,
        conversation_id: UUID,
        owner_id: UUID,
        messages: list[ChatMessage],
    ) -> AsyncIterator[str]:

        # --------------------------------------------------
        # Stage 1 - Extract user question
        # --------------------------------------------------

        if not messages:
            raise ValueError(
                "Conversation contains no messages."
            )

        user_prompt = messages[-1].content

        # --------------------------------------------------
        # Stage 2 - Retrieve relevant knowledge
        # --------------------------------------------------

        retrieval = await self._retrieval_service.retrieve(
            query=user_prompt,
            owner_id=owner_id,
        )

        # --------------------------------------------------
        # Stage 3 - Build prompt
        # --------------------------------------------------

        prompt_context = PromptContext(
            messages=messages,
            user_prompt=user_prompt,
            retrieved_chunks=retrieval.chunks,
        )

        chat_request = await self._prompt_builder.build(
            prompt_context,
        )

        # --------------------------------------------------
        # Stage 4 - Resolve provider
        # --------------------------------------------------

        provider = await self._chat_provider_resolver.resolve()

        # --------------------------------------------------
        # Stage 5 - Stream response
        # --------------------------------------------------

        async for chunk in provider.stream(chat_request):
            yield chunk.content