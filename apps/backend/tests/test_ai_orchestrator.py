import asyncio
from contextlib import contextmanager
from collections.abc import AsyncIterator
from uuid import UUID

from app.application.ai.dto.ai_stream_event import AIStreamEvent
from app.application.ai.orchestrator.ai_orchestrator import AIOrchestrator
from app.application.ai.services.context_assembler import ContextAssembler
from app.application.knowledge.contracts.chunk_metadata import ChunkMetadata
from app.application.knowledge.contracts.retrieved_chunk import RetrievedChunk
from app.application.knowledge.contracts.vector_search_result import (
    VectorSearchResult,
)
from app.domain.ai.models.chat_chunk import ChatChunk
from app.domain.ai.models.chat_message import ChatMessage
from app.domain.ai.models.chat_request import ChatRequest
from app.domain.ai.models.chat_usage import ChatUsage
from app.domain.conversation.enums.message_role import MessageRole
from app.infrastructure.observability.langfuse_observer import LangfuseObserver


DOCUMENT_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
OWNER_ID = UUID("11111111-1111-1111-1111-111111111111")


class StubRetrievalService:
    def __init__(self, chunks: list[RetrievedChunk]) -> None:
        self._chunks = chunks
        self.queries: list[str] = []

    async def retrieve(
        self,
        *,
        query: str,
        owner_id: UUID,
    ) -> VectorSearchResult:
        self.queries.append(query)
        return VectorSearchResult(chunks=self._chunks)


class StubPromptBuilder:
    def __init__(self) -> None:
        self.contexts = []

    async def build(self, context):
        self.contexts.append(context)
        return ChatRequest(messages=context.messages)


class StubProvider:
    def __init__(self) -> None:
        self.requests: list[ChatRequest] = []

    async def stream(self, request: ChatRequest) -> AsyncIterator[ChatChunk]:
        self.requests.append(request)
        yield ChatChunk(content="Grounded ")
        yield ChatChunk(content="answer")
        yield ChatChunk(
            content="",
            is_final=True,
            usage=ChatUsage(
                prompt_tokens=12,
                completion_tokens=4,
                total_tokens=16,
            ),
        )


class StubProviderResolver:
    def __init__(self, provider: StubProvider) -> None:
        self._provider = provider
        self.resolve_count = 0

    async def resolve(self) -> StubProvider:
        self.resolve_count += 1
        return self._provider


class RecordingGeneration:
    def __init__(self) -> None:
        self.updates: list[dict] = []

    def update(self, **kwargs) -> None:
        self.updates.append(kwargs)


class RecordingLangfuseClient:
    def __init__(self) -> None:
        self.generation = RecordingGeneration()
        self.arguments: dict = {}

    @contextmanager
    def start_as_current_observation(self, **kwargs):
        self.arguments = kwargs
        yield self.generation


def retrieved_chunk() -> RetrievedChunk:
    return RetrievedChunk(
        content="Approvals take five business days.",
        metadata=ChunkMetadata(
            document_id=DOCUMENT_ID,
            filename="approval-policy.pdf",
            chunk_id="approval-period",
            chunk_index=0,
            page_number=12,
            owner_id=OWNER_ID,
        ),
        score=0.91,
    )


async def collect_events(
    orchestrator: AIOrchestrator,
    prompt: str,
    on_completed=None,
) -> list[AIStreamEvent]:
    return [
        event
        async for event in orchestrator.respond(
            owner_id=OWNER_ID,
            messages=[
                ChatMessage(
                    role=MessageRole.USER,
                    content=prompt,
                )
            ],
            on_completed=on_completed,
        )
    ]


def create_orchestrator(
    chunks: list[RetrievedChunk],
    langfuse: LangfuseObserver | None = None,
):
    retrieval_service = StubRetrievalService(chunks)
    prompt_builder = StubPromptBuilder()
    provider = StubProvider()
    resolver = StubProviderResolver(provider)
    return (
        AIOrchestrator(
            retrieval_service=retrieval_service,
            context_assembler=ContextAssembler(max_tokens=100),
            prompt_builder=prompt_builder,
            chat_provider_resolver=resolver,
            langfuse=langfuse,
        ),
        prompt_builder,
        provider,
        resolver,
    )


def test_grounded_context_invokes_provider_streams_tokens_and_citations():
    orchestrator, prompt_builder, provider, resolver = create_orchestrator(
        [retrieved_chunk()]
    )

    events = asyncio.run(
        collect_events(orchestrator, "How long do approvals take?")
    )

    assert len(provider.requests) == 1
    assert resolver.resolve_count == 1
    assert prompt_builder.contexts[0].retrieved_chunks == [retrieved_chunk()]
    assert [event.type for event in events] == [
        "token",
        "token",
        "citations",
        "complete",
    ]
    assert [event.content for event in events[:2]] == ["Grounded ", "answer"]
    assert events[2].citations is not None
    assert [citation.chunk_id for citation in events[2].citations] == [
        "approval-period"
    ]


def test_no_context_returns_grounded_fallback_without_provider_resolution():
    orchestrator, prompt_builder, provider, resolver = create_orchestrator([])

    events = asyncio.run(
        collect_events(orchestrator, "What is the approval period?")
    )

    assert [event.type for event in events] == ["token", "complete"]
    assert events[0].content == (
        "I couldn't find enough information in the available knowledge "
        "base to answer that question."
    )
    assert prompt_builder.contexts == []
    assert provider.requests == []
    assert resolver.resolve_count == 0


def test_direct_conversation_without_context_uses_provider():
    orchestrator, prompt_builder, provider, resolver = create_orchestrator([])

    events = asyncio.run(collect_events(orchestrator, "Hello!"))

    assert len(prompt_builder.contexts) == 1
    assert prompt_builder.contexts[0].messages[-1].content == "Hello!"
    assert len(provider.requests) == 1
    assert resolver.resolve_count == 1
    assert [event.type for event in events] == ["token", "token", "complete"]


def test_streamed_response_publishes_completed_generation_evaluation_record():
    orchestrator, _, _, _ = create_orchestrator([retrieved_chunk()])
    records = []

    async def capture_record(record) -> None:
        records.append(record)

    events = asyncio.run(
        collect_events(
            orchestrator,
            "How long do approvals take?",
            on_completed=capture_record,
        )
    )

    assert [event.type for event in events] == [
        "token",
        "token",
        "citations",
        "complete",
    ]
    assert len(records) == 1
    assert records[0].question == "How long do approvals take?"
    assert records[0].answer == "Grounded answer"
    assert records[0].selected_chunks == [retrieved_chunk()]
    assert [citation.chunk_id for citation in records[0].citations] == [
        "approval-period"
    ]


def test_langfuse_generation_observes_streamed_generation_safely():
    client = RecordingLangfuseClient()
    observer = LangfuseObserver(
        client=client,
        enabled=True,
        capture_content=False,
    )
    orchestrator, _, _, _ = create_orchestrator(
        [retrieved_chunk()],
        langfuse=observer,
    )

    events = asyncio.run(
        collect_events(orchestrator, "How long do approvals take?")
    )

    assert [event.type for event in events] == [
        "token",
        "token",
        "citations",
        "complete",
    ]
    assert client.arguments["name"] == "rag.llm_generation"
    assert client.arguments["as_type"] == "generation"
    assert client.arguments["model"] == "gpt-4.1-mini"
    assert client.arguments["input"] is None
    assert client.generation.updates[0]["output"] is None
    assert client.generation.updates[0]["metadata"]["outcome"] == "success"
    assert client.generation.updates[0]["metadata"]["citation_event_present"] is True
    assert client.generation.updates[0]["usage_details"] == {
        "input": 12,
        "output": 4,
        "total": 16,
    }