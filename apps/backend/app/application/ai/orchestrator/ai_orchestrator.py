from collections.abc import AsyncIterator
from uuid import UUID

from app.application.ai.dto.ai_stream_event import (
    AIStreamEvent,
)
from app.application.ai.dto.prompt_context import (
    PromptContext,
)
from app.application.ai.ports.chat_provider_resolver import (
    ChatProviderResolver,
)
from app.application.ai.ports.prompt_builder import (
    PromptBuilder,
)
from app.application.ai.retrieval.document_retrieval_service import (
    DocumentRetrievalService,
)
from app.application.ai.services.citation_builder import (
    CitationBuilder,
)
from app.application.ai.services.prompt_logger import (
    PromptLogger,
)
from app.application.ai.services.retrieval_query_builder import (
    RetrievalQueryBuilder,
)
from app.domain.ai.models.chat_message import ChatMessage


class AIOrchestrator:
    """
    Coordinates the Enterprise AI execution pipeline.

    Pipeline
    --------
    1. Build retrieval query
    2. Retrieve relevant knowledge
    3. Build citations
    4. Build prompt
    5. Resolve provider
    6. Stream response
    7. Emit citations
    8. Emit completion event
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
        owner_id: UUID,
        messages: list[ChatMessage],
    ) -> AsyncIterator[AIStreamEvent]:
        """
        Executes the AI pipeline and emits structured
        streaming events.
        """

        # --------------------------------------------------
        # Stage 1 - Validate conversation messages
        # --------------------------------------------------

        if not messages:
            raise ValueError(
                "Conversation contains no messages."
            )

        # --------------------------------------------------
        # Stage 2 - Extract current user question
        # --------------------------------------------------

        user_prompt = messages[-1].content

        # --------------------------------------------------
        # Stage 3 - Build retrieval query
        # --------------------------------------------------

        retrieval_query = RetrievalQueryBuilder.build(
            messages=messages,
            user_prompt=user_prompt,
        )

        # --------------------------------------------------
        # Stage 4 - Retrieve relevant knowledge
        # --------------------------------------------------

        retrieval = await self._retrieval_service.retrieve(
            query=retrieval_query,
            owner_id=owner_id,
        )

        # --------------------------------------------------
        # Stage 5 - Build citations
        # --------------------------------------------------

        citations = CitationBuilder.build(
            retrieved_chunks=retrieval.chunks,
        )

        # --------------------------------------------------
        # Stage 6 - Build LLM prompt
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
        # Stage 7 - Prompt observability
        # --------------------------------------------------

        PromptLogger.log(chat_request)

        # --------------------------------------------------
        # Stage 8 - Resolve LLM provider
        # --------------------------------------------------

        provider = await self._chat_provider_resolver.resolve()

        # --------------------------------------------------
        # Stage 9 - Stream response
        # --------------------------------------------------

        async for chunk in provider.stream(chat_request):

            if chunk.is_final:
                break

            if not chunk.content:
                continue

            yield AIStreamEvent(
                type="token",
                content=chunk.content,
            )

        # --------------------------------------------------
        # Stage 10 - Emit citations
        # --------------------------------------------------

        if citations:
            yield AIStreamEvent(
                type="citations",
                citations=citations,
            )

        # --------------------------------------------------
        # Stage 11 - Emit completion
        # --------------------------------------------------

        yield AIStreamEvent(
            type="complete",
        )