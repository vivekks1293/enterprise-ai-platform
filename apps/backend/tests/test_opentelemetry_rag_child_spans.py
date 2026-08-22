import asyncio
from collections.abc import AsyncIterator
from uuid import UUID

import pytest
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

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
from app.domain.ai.models.chat_chunk import ChatChunk
from app.domain.ai.models.chat_message import ChatMessage
from app.domain.ai.models.chat_request import ChatRequest
from app.domain.conversation.enums.message_role import MessageRole


DOCUMENT_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
OWNER_ID = UUID("22222222-2222-2222-2222-222222222222")


EXPORTER = InMemorySpanExporter()
PROVIDER = TracerProvider(
    resource=Resource.create({"service.name": "child-span-tests"})
)
PROVIDER.add_span_processor(SimpleSpanProcessor(EXPORTER))
trace.set_tracer_provider(PROVIDER)


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


def clear_spans() -> None:
    EXPORTER.clear()


class StubEmbeddingProvider:
    async def embed_query(self, query: str) -> EmbeddingVector:
        return EmbeddingVector(values=[0.1])


class StubVectorStore:
    async def search(self, *, embedding, filter, top_k: int) -> VectorSearchResult:
        return VectorSearchResult(chunks=[chunk("semantic-a")])


class StubKeywordStore:
    async def search(self, *, query: str, filter, top_k: int) -> VectorSearchResult:
        return VectorSearchResult(chunks=[chunk("keyword-a")])


def test_retrieval_creates_mode_children_and_reranking_span():
    clear_spans()
    service = DocumentRetrievalService(
        embedding_provider=StubEmbeddingProvider(),
        vector_store=StubVectorStore(),
        keyword_store=StubKeywordStore(),
        reranker=None,
    )

    asyncio.run(
        service.retrieve(
            query="private query",
            owner_id=OWNER_ID,
            retrieval_mode="hybrid",
        )
    )

    spans = EXPORTER.get_finished_spans()
    names = {span.name for span in spans}
    assert {
        "rag.retrieval",
        "rag.retrieval.semantic",
        "rag.retrieval.keyword",
        "rag.retrieval.hybrid_rrf",
    } <= names
    retrieval_span = next(span for span in spans if span.name == "rag.retrieval")
    child_spans = [span for span in spans if span.parent is not None]
    assert all(span.context.trace_id == retrieval_span.context.trace_id for span in child_spans)
    assert retrieval_span.attributes["retrieval.mode"] == "hybrid"
    assert "private query" not in str(retrieval_span.attributes)


class StubRetrievalService:
    def __init__(self, chunks: list[RetrievedChunk]) -> None:
        self._chunks = chunks

    async def retrieve(self, *, query: str, owner_id: UUID) -> VectorSearchResult:
        return VectorSearchResult(chunks=self._chunks)


class StubPromptBuilder:
    async def build(self, context) -> ChatRequest:
        return ChatRequest(messages=context.messages)


class StreamingProvider:
    def __init__(self) -> None:
        self.active_span_names: list[str] = []

    async def stream(self, request: ChatRequest) -> AsyncIterator[ChatChunk]:
        self.active_span_names.append(trace.get_current_span().name)
        await asyncio.sleep(0)
        yield ChatChunk(content="answer")
        self.active_span_names.append(trace.get_current_span().name)
        yield ChatChunk(content="", is_final=True)


class FailingProvider:
    async def stream(self, request: ChatRequest) -> AsyncIterator[ChatChunk]:
        raise RuntimeError("provider failure")
        yield ChatChunk(content="")


class StubProviderResolver:
    def __init__(self, provider) -> None:
        self._provider = provider

    async def resolve(self):
        return self._provider


def create_orchestrator(chunks, provider) -> AIOrchestrator:
    return AIOrchestrator(
        retrieval_service=StubRetrievalService(chunks),
        context_assembler=ContextAssembler(max_tokens=100),
        prompt_builder=StubPromptBuilder(),
        chat_provider_resolver=StubProviderResolver(provider),
    )


async def collect_events(orchestrator: AIOrchestrator, prompt: str):
    return [
        event
        async for event in orchestrator.respond(
            owner_id=OWNER_ID,
            messages=[ChatMessage(role=MessageRole.USER, content=prompt)],
        )
    ]


def test_orchestrator_creates_children_with_shared_trace_and_distinct_ids():
    clear_spans()
    provider = StreamingProvider()

    events = asyncio.run(
        collect_events(create_orchestrator([chunk("selected")], provider), "question")
    )

    assert [event.type for event in events] == [
        "token",
        "citations",
        "complete",
    ]
    assert provider.active_span_names == [
        "rag.llm_generation",
        "rag.llm_generation",
    ]
    spans = EXPORTER.get_finished_spans()
    names = {span.name for span in spans}
    assert {
        "rag.orchestrate",
        "rag.context_assembly",
        "rag.prompt_construction",
        "rag.llm_generation",
    } <= names
    root = next(span for span in spans if span.name == "rag.orchestrate")
    children = [span for span in spans if span.name != "rag.orchestrate"]
    assert all(span.context.trace_id == root.context.trace_id for span in children)
    assert len({span.context.span_id for span in spans}) == len(spans)
    llm_span = next(span for span in spans if span.name == "rag.llm_generation")
    assert llm_span.attributes["llm.time_to_first_token_ms"] >= 0
    assert llm_span.attributes["llm.token_event_count"] == 1
    assert "question" not in str(llm_span.attributes)


def test_provider_failure_marks_llm_span_error_without_swallowing_exception():
    clear_spans()

    with pytest.raises(RuntimeError, match="provider failure"):
        asyncio.run(
            collect_events(create_orchestrator([chunk("selected")], FailingProvider()), "question")
        )

    llm_span = next(
        span for span in EXPORTER.get_finished_spans() if span.name == "rag.llm_generation"
    )
    assert llm_span.status.status_code.name == "ERROR"
    assert llm_span.attributes["llm.outcome"] == "failure"
    assert "provider failure" not in str(llm_span.events)


def test_no_context_fallback_has_no_llm_generation_span():
    clear_spans()

    events = asyncio.run(
        collect_events(create_orchestrator([], StreamingProvider()), "knowledge question")
    )

    assert [event.type for event in events] == ["token", "complete"]
    assert all(
        span.name != "rag.llm_generation"
        for span in EXPORTER.get_finished_spans()
    )