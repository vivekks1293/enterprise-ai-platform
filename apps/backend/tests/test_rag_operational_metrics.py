import asyncio
from collections.abc import AsyncIterator
from uuid import UUID

import pytest

from app.application.ai.orchestrator.ai_orchestrator import AIOrchestrator
from app.application.ai.retrieval.document_retrieval_service import (
    DocumentRetrievalService,
)
from app.application.ai.services.context_assembler import ContextAssembler
from app.application.knowledge.contracts.chunk_metadata import ChunkMetadata
from app.application.knowledge.contracts.embedding_vector import EmbeddingVector
from app.application.knowledge.contracts.retrieved_chunk import RetrievedChunk
from app.application.knowledge.contracts.vector_search_result import (
    VectorSearchResult,
)
from app.core.config.settings import settings
from app.domain.ai.models.chat_chunk import ChatChunk
from app.domain.ai.models.chat_message import ChatMessage
from app.domain.ai.models.chat_request import ChatRequest
from app.domain.conversation.enums.message_role import MessageRole
from app.infrastructure.observability.in_memory_metrics_recorder import (
    InMemoryMetricsRecorder,
)


DOCUMENT_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
OWNER_ID = UUID("22222222-2222-2222-2222-222222222222")


def chunk(chunk_id: str) -> RetrievedChunk:
    return RetrievedChunk(
        content=f"Content for {chunk_id}",
        metadata=ChunkMetadata(
            document_id=DOCUMENT_ID,
            filename="private.pdf",
            chunk_id=chunk_id,
            chunk_index=0,
            page_number=1,
            owner_id=OWNER_ID,
        ),
        score=0.9,
    )


class StubEmbeddingProvider:
    async def embed_query(self, query: str) -> EmbeddingVector:
        return EmbeddingVector(values=[0.1])


class StubVectorStore:
    async def search(self, *, embedding, filter, top_k: int) -> VectorSearchResult:
        return VectorSearchResult(chunks=[chunk("semantic-a"), chunk("semantic-b")])


class StubKeywordStore:
    async def search(self, *, query: str, filter, top_k: int) -> VectorSearchResult:
        return VectorSearchResult(chunks=[chunk("keyword-a")])


class StubReranker:
    def rerank(self, *, query: str, chunks, top_k: int) -> VectorSearchResult:
        return VectorSearchResult(chunks=chunks[:1])


def test_retrieval_metrics_distinguish_hybrid_candidates_and_final_results():
    metrics = InMemoryMetricsRecorder()
    service = DocumentRetrievalService(
        embedding_provider=StubEmbeddingProvider(),
        vector_store=StubVectorStore(),
        keyword_store=StubKeywordStore(),
        reranker=StubReranker(),
        metrics=metrics,
    )

    result = asyncio.run(
        service.retrieve(
            query="private query",
            owner_id=OWNER_ID,
            top_k=1,
            retrieval_mode="hybrid",
        )
    )

    labels = {"retrieval_mode": "hybrid"}
    assert len(result.chunks) == 1
    assert metrics.observations("rag_hybrid_semantic_candidates", labels=labels) == [2]
    assert metrics.observations("rag_hybrid_keyword_candidates", labels=labels) == [1]
    assert metrics.observations("rag_hybrid_fused_candidates", labels=labels) == [3]
    assert metrics.observations("rag_retrieval_candidates", labels=labels) == [3]
    assert metrics.observations("rag_retrieval_results", labels=labels) == [1]
    assert len(metrics.observations("rag_retrieval_duration_ms", labels=labels)) == 1
    assert len(
        metrics.observations(
            "rag_reranking_duration_ms",
            labels={"reranker_type": "StubReranker"},
        )
    ) == 1


class StubRetrievalService:
    def __init__(self, chunks: list[RetrievedChunk]) -> None:
        self._chunks = chunks

    async def retrieve(self, *, query: str, owner_id: UUID) -> VectorSearchResult:
        return VectorSearchResult(chunks=self._chunks)


class StubPromptBuilder:
    async def build(self, context) -> ChatRequest:
        return ChatRequest(messages=context.messages)


class StreamingProvider:
    async def stream(self, request: ChatRequest) -> AsyncIterator[ChatChunk]:
        await asyncio.sleep(0)
        yield ChatChunk(content="Grounded ")
        yield ChatChunk(content="answer")
        yield ChatChunk(content="", is_final=True)


class FailingProvider:
    async def stream(self, request: ChatRequest) -> AsyncIterator[ChatChunk]:
        raise RuntimeError("provider unavailable")
        yield ChatChunk(content="")


class StubProviderResolver:
    def __init__(self, provider) -> None:
        self._provider = provider

    async def resolve(self):
        return self._provider


def create_orchestrator(
    chunks: list[RetrievedChunk],
    provider,
    metrics: InMemoryMetricsRecorder,
) -> AIOrchestrator:
    return AIOrchestrator(
        retrieval_service=StubRetrievalService(chunks),
        context_assembler=ContextAssembler(max_tokens=100, metrics=metrics),
        prompt_builder=StubPromptBuilder(),
        chat_provider_resolver=StubProviderResolver(provider),
        metrics=metrics,
    )


async def collect_events(orchestrator: AIOrchestrator, prompt: str):
    return [
        event
        async for event in orchestrator.respond(
            owner_id=OWNER_ID,
            messages=[ChatMessage(role=MessageRole.USER, content=prompt)],
        )
    ]


def test_successful_stream_records_one_success_and_latency_metrics():
    metrics = InMemoryMetricsRecorder()
    events = asyncio.run(
        collect_events(
            create_orchestrator([chunk("selected")], StreamingProvider(), metrics),
            "What is the answer?",
        )
    )

    request_labels = {"retrieval_mode": "semantic", "outcome": "success"}
    provider_labels = {
        "provider": "StreamingProvider",
        "model": settings.openai_chat_model,
    }
    assert [event.type for event in events] == [
        "token",
        "token",
        "citations",
        "complete",
    ]
    assert metrics.counter_value("rag_requests_total", labels={"retrieval_mode": "semantic"}) == 1
    assert metrics.counter_value("rag_requests_success_total", labels=request_labels) == 1
    assert metrics.counter_value("rag_requests_failed_total", labels=request_labels) == 0
    assert len(metrics.observations("rag_request_duration_ms", labels=request_labels)) == 1
    assert len(metrics.observations("rag_context_assembly_duration_ms")) == 1
    assert metrics.observations("rag_context_selected_chunks") == [1]
    assert len(metrics.observations("rag_prompt_construction_duration_ms")) == 1
    assert len(metrics.observations("rag_llm_ttft_ms", labels=provider_labels)) == 1
    assert len(
        metrics.observations("rag_llm_generation_duration_ms", labels=provider_labels)
    ) == 1
    assert metrics.counter_value("rag_llm_token_events", labels=provider_labels) == 2


def test_fallback_records_only_one_fallback_outcome_without_llm_metrics():
    metrics = InMemoryMetricsRecorder()

    events = asyncio.run(
        collect_events(
            create_orchestrator([], StreamingProvider(), metrics),
            "What is the answer?",
        )
    )

    fallback_labels = {"retrieval_mode": "semantic", "outcome": "fallback"}
    assert [event.type for event in events] == ["token", "complete"]
    assert metrics.counter_value("rag_requests_total", labels={"retrieval_mode": "semantic"}) == 1
    assert metrics.counter_value("rag_requests_fallback_total", labels=fallback_labels) == 1
    assert metrics.counter_value(
        "rag_requests_success_total",
        labels={"retrieval_mode": "semantic", "outcome": "success"},
    ) == 0
    assert metrics.observations("rag_llm_ttft_ms") == []
    assert metrics.observations("rag_llm_generation_duration_ms") == []


def test_failed_stream_records_one_failure_without_fake_ttft():
    metrics = InMemoryMetricsRecorder()
    orchestrator = create_orchestrator([chunk("selected")], FailingProvider(), metrics)

    with pytest.raises(RuntimeError, match="provider unavailable"):
        asyncio.run(collect_events(orchestrator, "What is the answer?"))

    failure_labels = {"retrieval_mode": "semantic", "outcome": "failed"}
    assert metrics.counter_value("rag_requests_failed_total", labels=failure_labels) == 1
    assert metrics.counter_value("rag_requests_success_total", labels={
        "retrieval_mode": "semantic",
        "outcome": "success",
    }) == 0
    assert metrics.observations("rag_llm_ttft_ms") == []
    assert len(
        metrics.observations(
            "rag_llm_generation_duration_ms",
            labels={
                "provider": "FailingProvider",
                "model": settings.openai_chat_model,
            },
        )
    ) == 1


def test_metrics_reject_high_cardinality_identifiers_as_labels():
    metrics = InMemoryMetricsRecorder()

    for forbidden_label in ("request_id", "user_id", "document_id", "query"):
        with pytest.raises(ValueError, match="High-cardinality"):
            metrics.increment("rag_requests_total", labels={forbidden_label: "value"})