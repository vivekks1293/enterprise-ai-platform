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
from app.application.common.ports.metrics_recorder import (
    MetricsRecorder,
    NullMetricsRecorder,
)
from app.domain.ai.models.citation import Citation
from app.domain.ai.models.chat_message import ChatMessage
from app.domain.ai.models.chat_usage import ChatUsage
from app.core.config.settings import settings
from app.core.logging.logger import log_event
from app.infrastructure.observability.langfuse_observer import (
    LangfuseObserver,
)
from app.evaluation.contracts.generation_evaluation_record import (
    GenerationEvaluationRecord,
)
from app.core.telemetry.opentelemetry import mark_span_error, tracer


import logging


logger = logging.getLogger(__name__)


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
        metrics: MetricsRecorder | None = None,
        langfuse: LangfuseObserver | None = None,
    ) -> None:
        self._retrieval_service = retrieval_service
        self._context_assembler = context_assembler
        self._prompt_builder = prompt_builder
        self._chat_provider_resolver = chat_provider_resolver
        self._metrics = metrics or NullMetricsRecorder()
        self._langfuse = langfuse or LangfuseObserver()

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

        with tracer.start_as_current_span("rag.orchestrate") as span:
            try:
                async for event in self._respond(
                    owner_id=owner_id,
                    messages=messages,
                    on_completed=on_completed,
                ):
                    yield event
            except Exception as exc:
                mark_span_error(span, exc)
                raise

    async def _respond(
        self,
        *,
        owner_id: UUID,
        messages: list[ChatMessage],
        on_completed: (
            Callable[[GenerationEvaluationRecord], Awaitable[None]] | None
        ) = None,
    ) -> AsyncIterator[AIStreamEvent]:
        orchestration_started_at = perf_counter()
        retrieval_mode = "semantic"
        context_count = 0
        citation_count = 0
        generation_status = "failed"
        outcome_recorded = False

        # --------------------------------------------------
        # Stage 1 - Validate conversation messages
        # --------------------------------------------------

        if not messages:
            self._metrics.increment(
                "rag_requests_total",
                labels={"retrieval_mode": retrieval_mode},
            )
            self._record_request_outcome(
                outcome="failed",
                retrieval_mode=retrieval_mode,
                duration_ms=self._duration_ms(orchestration_started_at),
            )
            raise ValueError(
                "Conversation contains no messages."
            )

        self._metrics.increment(
            "rag_requests_total",
            labels={"retrieval_mode": retrieval_mode},
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

        try:
            retrieval = await self._retrieval_service.retrieve(
                query=retrieval_query,
                owner_id=owner_id,
            )

        # --------------------------------------------------
        # Stage 5 - Assemble bounded context
        # --------------------------------------------------

            context_started_at = perf_counter()
            try:
                selected_chunks = self._context_assembler.assemble(
                    retrieval.chunks,
                )
            except Exception as exc:
                log_event(
                    logger,
                    "rag.context_assembly.failed",
                    stage="context_assembly",
                    exception_type=type(exc).__name__,
                    duration_ms=self._duration_ms(context_started_at),
                )
                raise
            context_count = len(selected_chunks)

            if (
                not selected_chunks
                and not self._is_direct_conversational_request(user_prompt)
            ):
                generation_status = "fallback"
                log_event(
                    logger,
                    "llm.generation.fallback",
                    stage="llm_generation",
                    provider=None,
                    model=None,
                    token_event_count=0,
                    citation_event_present=False,
                    completion_status="fallback",
                    duration_ms=0.0,
                )
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
                self._log_orchestration_completed(
                    started_at=orchestration_started_at,
                    retrieval_mode=retrieval_mode,
                    context_count=context_count,
                    citation_count=0,
                    generation_status=generation_status,
                )
                self._record_request_outcome(
                    outcome="fallback",
                    retrieval_mode=retrieval_mode,
                    duration_ms=self._duration_ms(orchestration_started_at),
                )
                outcome_recorded = True
                yield AIStreamEvent(type="complete")
                return

        # --------------------------------------------------
        # Stage 6 - Build citations
        # --------------------------------------------------

            citations = CitationBuilder.build(
                retrieved_chunks=selected_chunks,
            )
            citation_count = len(citations)

        # --------------------------------------------------
        # Stage 7 - Build LLM prompt
        # --------------------------------------------------

            prompt_context = PromptContext(
                messages=messages,
                user_prompt=user_prompt,
                retrieved_chunks=selected_chunks,
            )

            prompt_started_at = perf_counter()
            with tracer.start_as_current_span("rag.prompt_construction") as prompt_span:
                try:
                    chat_request = await self._prompt_builder.build(
                        prompt_context,
                    )
                except Exception as exc:
                    mark_span_error(prompt_span, exc)
                    log_event(
                        logger,
                        "rag.prompt_construction.failed",
                        stage="prompt_construction",
                        exception_type=type(exc).__name__,
                        duration_ms=self._duration_ms(prompt_started_at),
                    )
                    raise
                prompt_span.set_attributes(
                    {
                        "prompt.message_count": len(chat_request.messages),
                        "prompt.context_item_count": len(selected_chunks),
                        "prompt.estimated_input_size": sum(
                            len(message.content) for message in chat_request.messages
                        ),
                    }
                )
                prompt_duration_ms = self._duration_ms(prompt_started_at)
                prompt_span.set_attribute("prompt.duration_ms", prompt_duration_ms)

        # --------------------------------------------------
        # Stage 7 - Prompt observability
        # --------------------------------------------------

            PromptLogger.log(
                chat_request,
                context_item_count=len(selected_chunks),
                duration_ms=prompt_duration_ms,
            )
            self._metrics.observe(
                "rag_prompt_construction_duration_ms",
                prompt_duration_ms,
            )

        # --------------------------------------------------
        # Stage 8 - Resolve LLM provider
        # --------------------------------------------------

            provider = await self._chat_provider_resolver.resolve()

        # --------------------------------------------------
        # Stage 9 - Stream response
        # --------------------------------------------------

            answer_parts: list[str] = []
            generation_started_at = perf_counter()
            first_token_at: float | None = None
            token_event_count = 0
            usage: ChatUsage | None = None

            with tracer.start_as_current_span("rag.llm_generation") as llm_span:
                llm_span.set_attributes(
                    {
                        "llm.provider": type(provider).__name__,
                        "llm.model": settings.openai_chat_model,
                    }
                )
                with self._langfuse.start_generation(
                    provider=type(provider).__name__,
                    model=settings.openai_chat_model,
                    input_content=(
                        [
                            {
                                "role": str(message.role),
                                "content": message.content,
                            }
                            for message in chat_request.messages
                        ]
                        if self._langfuse.capture_content
                        else None
                    ),
                ) as langfuse_generation:
                    try:
                        async for chunk in provider.stream(chat_request):

                            if chunk.is_final:
                                usage = chunk.usage or usage
                                break

                            if not chunk.content:
                                usage = chunk.usage or usage
                                continue

                            usage = chunk.usage or usage
                            if first_token_at is None:
                                first_token_at = perf_counter()
                                self._metrics.observe(
                                    "rag_llm_ttft_ms",
                                    self._duration_ms(
                                        generation_started_at,
                                        first_token_at,
                                    ),
                                    labels=self._provider_labels(provider),
                                )
                            token_event_count += 1
                            self._metrics.increment(
                                "rag_llm_token_events",
                                labels=self._provider_labels(provider),
                            )
                            answer_parts.append(chunk.content)

                            yield AIStreamEvent(
                                type="token",
                                content=chunk.content,
                            )
                    except Exception as exc:
                        mark_span_error(llm_span, exc)
                        generation_status = "failed"
                        generation_duration_ms = self._duration_ms(generation_started_at)
                        self._langfuse.update_generation(
                            langfuse_generation,
                            output="".join(answer_parts),
                            metadata={
                                "token_event_count": token_event_count,
                                "outcome": "failure",
                            },
                            usage_details=self._langfuse_usage_details(usage),
                            level="ERROR",
                            status_message=type(exc).__name__,
                        )
                        llm_span.set_attributes(
                            {
                                "llm.duration_ms": generation_duration_ms,
                                "llm.token_event_count": token_event_count,
                                "llm.outcome": "failure",
                            }
                        )
                        log_event(
                            logger,
                            "llm.generation.failed",
                            stage="llm_generation",
                            provider=type(provider).__name__,
                            model=settings.openai_chat_model,
                            token_event_count=token_event_count,
                            exception_type=type(exc).__name__,
                            duration_ms=generation_duration_ms,
                        )
                        self._metrics.observe(
                            "rag_llm_generation_duration_ms",
                            generation_duration_ms,
                            labels=self._provider_labels(provider),
                        )
                        raise

                generation_completed_at = perf_counter()
                generation_duration_ms = self._duration_ms(
                    generation_started_at,
                    generation_completed_at,
                )
                llm_span.set_attributes(
                    {
                        "llm.time_to_first_token_ms": (
                            self._duration_ms(generation_started_at, first_token_at)
                            if first_token_at is not None
                            else None
                        ),
                        "llm.duration_ms": generation_duration_ms,
                        "llm.token_event_count": token_event_count,
                        "llm.citation_event_present": bool(citations),
                        "llm.outcome": "success",
                    }
                )
                self._langfuse.update_generation(
                    langfuse_generation,
                    output="".join(answer_parts),
                    metadata={
                        "time_to_first_token_ms": (
                            self._duration_ms(generation_started_at, first_token_at)
                            if first_token_at is not None
                            else None
                        ),
                        "duration_ms": generation_duration_ms,
                        "token_event_count": token_event_count,
                        "citation_event_present": bool(citations),
                        "outcome": "success",
                    },
                    usage_details=self._langfuse_usage_details(usage),
                )

                if citations:
                    yield AIStreamEvent(
                        type="citations",
                        citations=citations,
                    )

                generation_status = "completed"
                log_event(
                    logger,
                    "llm.generation.completed",
                    stage="llm_generation",
                    provider=type(provider).__name__,
                    model=settings.openai_chat_model,
                    time_to_first_token_ms=(
                        self._duration_ms(generation_started_at, first_token_at)
                        if first_token_at is not None
                        else None
                    ),
                    total_generation_duration_ms=generation_duration_ms,
                    token_event_count=token_event_count,
                    input_tokens=(usage.prompt_tokens if usage else None),
                    output_tokens=(usage.completion_tokens if usage else None),
                    total_tokens=(usage.total_tokens if usage else None),
                    citation_event_present=bool(citations),
                    completion_status="completed",
                )
                self._metrics.observe(
                    "rag_llm_generation_duration_ms",
                    generation_duration_ms,
                    labels=self._provider_labels(provider),
                )

                await self._publish_evaluation_record(
                    on_completed=on_completed,
                    question=user_prompt,
                    answer="".join(answer_parts),
                    selected_chunks=selected_chunks,
                    citations=citations,
                )

                self._log_orchestration_completed(
                    started_at=orchestration_started_at,
                    retrieval_mode=retrieval_mode,
                    context_count=context_count,
                    citation_count=citation_count,
                    generation_status=generation_status,
                )
                self._record_request_outcome(
                    outcome="success",
                    retrieval_mode=retrieval_mode,
                    duration_ms=self._duration_ms(orchestration_started_at),
                )
                outcome_recorded = True

                yield AIStreamEvent(
                    type="complete",
                )
        except Exception as exc:
            log_event(
                logger,
                "rag.orchestration.failed",
                stage="rag_orchestrate",
                retrieval_mode=retrieval_mode,
                context_count=context_count,
                citation_count=citation_count,
                generation_status=generation_status,
                exception_type=type(exc).__name__,
                duration_ms=self._duration_ms(orchestration_started_at),
            )
            if not outcome_recorded:
                self._record_request_outcome(
                    outcome="failed",
                    retrieval_mode=retrieval_mode,
                    duration_ms=self._duration_ms(orchestration_started_at),
                )
            raise

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
    def _duration_ms(started_at: float, ended_at: float | None = None) -> float:
        return round(((ended_at or perf_counter()) - started_at) * 1000, 2)

    @staticmethod
    def _log_orchestration_completed(
        *,
        started_at: float,
        retrieval_mode: str,
        context_count: int,
        citation_count: int,
        generation_status: str,
    ) -> None:
        log_event(
            logger,
            "rag.orchestration.completed",
            stage="rag_orchestrate",
            duration_ms=AIOrchestrator._duration_ms(started_at),
            retrieval_mode=retrieval_mode,
            context_count=context_count,
            citation_count=citation_count,
            generation_status=generation_status,
        )

    def _record_request_outcome(
        self,
        *,
        outcome: str,
        retrieval_mode: str,
        duration_ms: float,
    ) -> None:
        self._metrics.increment(
            f"rag_requests_{outcome}_total",
            labels={"retrieval_mode": retrieval_mode, "outcome": outcome},
        )
        self._metrics.observe(
            "rag_request_duration_ms",
            duration_ms,
            labels={"retrieval_mode": retrieval_mode, "outcome": outcome},
        )

    @staticmethod
    def _provider_labels(provider: object) -> dict[str, str]:
        return {
            "provider": type(provider).__name__,
            "model": settings.openai_chat_model,
        }

    @staticmethod
    def _langfuse_usage_details(
        usage: ChatUsage | None,
    ) -> dict[str, int] | None:
        if usage is None:
            return None

        values = {
            "input": usage.prompt_tokens,
            "output": usage.completion_tokens,
            "total": usage.total_tokens,
        }
        available_values = {
            key: value
            for key, value in values.items()
            if value is not None
        }
        return available_values or None

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