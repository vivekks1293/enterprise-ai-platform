import asyncio
import logging
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
from app.core.logging.logger import request_id_context
from app.domain.ai.models.chat_chunk import ChatChunk
from app.domain.ai.models.chat_message import ChatMessage
from app.domain.ai.models.chat_request import ChatRequest
from app.domain.conversation.enums.message_role import MessageRole


REQUEST_ID = "11111111-1111-1111-1111-111111111111"
DOCUMENT_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
OWNER_ID = UUID("22222222-2222-2222-2222-222222222222")


def event_records(caplog, event: str):
    return [record for record in caplog.records if record.getMessage() == event]


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


def create_retrieval_service(reranker=None) -> DocumentRetrievalService:
    return DocumentRetrievalService(
        embedding_provider=StubEmbeddingProvider(),
        vector_store=StubVectorStore(),
        keyword_store=StubKeywordStore(),
        reranker=reranker,
    )


@pytest.mark.parametrize(
    ("mode", "event"),
    [
        ("semantic", "retrieval.semantic_search.completed"),
        ("keyword", "retrieval.keyword_search.completed"),
    ],
)
def test_individual_retrieval_modes_emit_safe_result_telemetry(caplog, mode, event):
    caplog.set_level(logging.INFO)
    request_token = request_id_context.set(REQUEST_ID)
    try:
        result = asyncio.run(
            create_retrieval_service().retrieve(
                query="sensitive query",
                owner_id=OWNER_ID,
                retrieval_mode=mode,
            )
        )
    finally:
        request_id_context.reset(request_token)

    record = event_records(caplog, event)[0]
    assert record.request_id == REQUEST_ID
    assert record.retrieval_mode == mode
    assert record.result_count == len(result.chunks)
    assert record.duration_ms >= 0


def test_hybrid_and_reranking_emit_candidate_and_count_telemetry(caplog):
    caplog.set_level(logging.INFO)

    asyncio.run(
        create_retrieval_service(StubReranker()).retrieve(
            query="sensitive query",
            owner_id=OWNER_ID,
            top_k=1,
            retrieval_mode="hybrid",
        )
    )

    hybrid_record = event_records(caplog, "retrieval.hybrid_rrf.completed")[0]
    rerank_record = event_records(caplog, "retrieval.reranking.completed")[0]
    assert hybrid_record.semantic_candidate_count == 2
    assert hybrid_record.keyword_candidate_count == 1
    assert hybrid_record.fused_candidate_count == 3
    assert hybrid_record.duration_ms >= 0
    assert rerank_record.input_count == 3
    assert rerank_record.output_count == 1
    assert rerank_record.reranker_type == "StubReranker"


def test_context_assembly_emits_budget_and_selection_telemetry(caplog):
    caplog.set_level(logging.INFO)

    selected = ContextAssembler(max_tokens=4).assemble(
        [chunk("first"), chunk("first"), chunk("excluded")]
    )

    record = event_records(caplog, "context.assembled")[0]
    assert len(selected) == 1
    assert record.candidate_count == 3
    assert record.selected_count == 1
    assert record.excluded_count == 2
    assert record.duplicate_count == 1
    assert record.configured_context_budget == 4


class StubRetrievalService:
    def __init__(self, chunks: list[RetrievedChunk]) -> None:
        self._chunks = chunks

    async def retrieve(self, *, query: str, owner_id: UUID) -> VectorSearchResult:
        return VectorSearchResult(chunks=self._chunks)


class StubPromptBuilder:
    async def build(self, context) -> ChatRequest:
        return ChatRequest(messages=context.messages)


class StubProvider:
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


async def collect_events(orchestrator: AIOrchestrator, prompt: str):
    return [
        event
        async for event in orchestrator.respond(
            owner_id=OWNER_ID,
            messages=[ChatMessage(role=MessageRole.USER, content=prompt)],
        )
    ]


def create_orchestrator(chunks: list[RetrievedChunk], provider) -> AIOrchestrator:
    return AIOrchestrator(
        retrieval_service=StubRetrievalService(chunks),
        context_assembler=ContextAssembler(max_tokens=100),
        prompt_builder=StubPromptBuilder(),
        chat_provider_resolver=StubProviderResolver(provider),
    )


def test_generation_records_ttft_total_and_correlated_rag_completion(caplog):
    caplog.set_level(logging.INFO)
    request_token = request_id_context.set(REQUEST_ID)
    try:
        events = asyncio.run(
            collect_events(
                create_orchestrator([chunk("selected")], StubProvider()),
                "What is the answer?",
            )
        )
    finally:
        request_id_context.reset(request_token)

    generation_record = event_records(caplog, "llm.generation.completed")[0]
    orchestration_record = event_records(caplog, "rag.orchestration.completed")[0]
    assert [event.type for event in events] == [
        "token",
        "token",
        "citations",
        "complete",
    ]
    assert generation_record.request_id == REQUEST_ID
    assert generation_record.time_to_first_token_ms is not None
    assert generation_record.total_generation_duration_ms >= generation_record.time_to_first_token_ms
    assert generation_record.token_event_count == 2
    assert generation_record.citation_event_present is True
    assert orchestration_record.request_id == REQUEST_ID
    assert orchestration_record.generation_status == "completed"


def test_no_context_fallback_does_not_report_provider_generation(caplog):
    caplog.set_level(logging.INFO)

    events = asyncio.run(
        collect_events(
            create_orchestrator([], StubProvider()),
            "What is the answer?",
        )
    )

    assert [event.type for event in events] == ["token", "complete"]
    assert event_records(caplog, "llm.generation.completed") == []
    fallback_record = event_records(caplog, "llm.generation.fallback")[0]
    assert fallback_record.completion_status == "fallback"
    assert fallback_record.provider is None


def test_provider_failure_records_safe_generation_and_orchestration_events(caplog):
    caplog.set_level(logging.INFO)
    orchestrator = create_orchestrator([chunk("selected")], FailingProvider())

    with pytest.raises(RuntimeError, match="provider unavailable"):
        asyncio.run(collect_events(orchestrator, "What is the answer?"))

    generation_record = event_records(caplog, "llm.generation.failed")[0]
    orchestration_record = event_records(caplog, "rag.orchestration.failed")[0]
    assert generation_record.exception_type == "RuntimeError"
    assert generation_record.token_event_count == 0
    assert orchestration_record.generation_status == "failed"