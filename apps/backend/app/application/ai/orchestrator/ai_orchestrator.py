from collections.abc import AsyncIterator, Awaitable, Callable
from time import perf_counter
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
from app.application.ai.services.context_assembler import (
    ContextAssembler,
)
from app.application.ai.services.prompt_logger import (
    PromptLogger,
)
from app.application.ai.services.retrieval_query_builder import (
    RetrievalQueryBuilder,
)
from app.application.knowledge.contracts.retrieved_chunk import (
    RetrievedChunk,
)
from app.domain.ai.models.citation import Citation
from app.domain.ai.models.chat_message import ChatMessage
from app.evaluation.contracts.generation_evaluation_record import (
    GenerationEvaluationRecord,
)


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

    _NO_CONTEXT_FALLBACK = (
        "I couldn't find enough information in the available knowledge "
        "base to answer that question."
    )
    _DIRECT_CONVERSATIONAL_PROMPTS = frozenset(
        {
            "hello",
            "hi",
            "hey",
            "good morning",
            "good afternoon",
            "good evening",
            "how are you",
            "thanks",
            "thank you",
            "bye",
            "goodbye",
        }
    )

    def __init__(
        self,
        retrieval_service: DocumentRetrievalService,
        context_assembler: ContextAssembler,
        prompt_builder: PromptBuilder,
        chat_provider_resolver: ChatProviderResolver,
    ) -> None:
        self._retrieval_service = retrieval_service
        self._context_assembler = context_assembler
        self._prompt_builder = prompt_builder
        self._chat_provider_resolver = chat_provider_resolver

    async def respond(
        self,
        *,
        owner_id: UUID,
        messages: list[ChatMessage],
        on_completed: (
            Callable[[GenerationEvaluationRecord], Awaitable[None]] | None
        ) = None,
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
        # Stage 5 - Assemble bounded context
        # --------------------------------------------------

        selected_chunks = self._context_assembler.assemble(
            retrieval.chunks,
        )

        if (
            not selected_chunks
            and not self._is_direct_conversational_request(user_prompt)
        ):
            yield AIStreamEvent(
                type="token",
                content=self._NO_CONTEXT_FALLBACK,
            )
            await self._publish_evaluation_record(
                on_completed=on_completed,
                question=user_prompt,
                answer=self._NO_CONTEXT_FALLBACK,
                selected_chunks=selected_chunks,
                citations=[],
            )
            yield AIStreamEvent(type="complete")
            return

        # --------------------------------------------------
        # Stage 6 - Build citations
        # --------------------------------------------------

        citations = CitationBuilder.build(
            retrieved_chunks=selected_chunks,
        )

        # --------------------------------------------------
        # Stage 7 - Build LLM prompt
        # --------------------------------------------------

        prompt_context = PromptContext(
            messages=messages,
            user_prompt=user_prompt,
            retrieved_chunks=selected_chunks,
        )

        prompt_started_at = perf_counter()
        chat_request = await self._prompt_builder.build(
            prompt_context,
        )

        # --------------------------------------------------
        # Stage 7 - Prompt observability
        # --------------------------------------------------

        PromptLogger.log(
            chat_request,
            context_item_count=len(selected_chunks),
            duration_ms=round(
                (perf_counter() - prompt_started_at) * 1000,
                2,
            ),
        )

        # --------------------------------------------------
        # Stage 8 - Resolve LLM provider
        # --------------------------------------------------

        provider = await self._chat_provider_resolver.resolve()

        # --------------------------------------------------
        # Stage 9 - Stream response
        # --------------------------------------------------

        answer_parts: list[str] = []

        async for chunk in provider.stream(chat_request):

            if chunk.is_final:
                break

            if not chunk.content:
                continue

            answer_parts.append(chunk.content)

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

        await self._publish_evaluation_record(
            on_completed=on_completed,
            question=user_prompt,
            answer="".join(answer_parts),
            selected_chunks=selected_chunks,
            citations=citations,
        )

        # --------------------------------------------------
        # Stage 11 - Emit completion
        # --------------------------------------------------

        yield AIStreamEvent(
            type="complete",
        )

    @classmethod
    def _is_direct_conversational_request(cls, user_prompt: str) -> bool:
        """Allows explicit social turns to use the normal provider path."""

        normalized_prompt = " ".join(
            "".join(
                character
                for character in user_prompt.lower()
                if character.isalnum() or character.isspace()
            ).split()
        )
        return normalized_prompt in cls._DIRECT_CONVERSATIONAL_PROMPTS

    @staticmethod
    async def _publish_evaluation_record(
        *,
        on_completed: Callable[[GenerationEvaluationRecord], Awaitable[None]] | None,
        question: str,
        answer: str,
        selected_chunks: list[RetrievedChunk],
        citations: list[Citation],
    ) -> None:
        if on_completed is None:
            return

        await on_completed(
            GenerationEvaluationRecord(
                question=question,
                answer=answer,
                selected_chunks=selected_chunks,
                citations=citations,
            )
        )