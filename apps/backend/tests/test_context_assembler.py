import asyncio
from uuid import UUID

import pytest

from app.application.ai.dto.prompt_context import PromptContext
from app.application.ai.services.citation_builder import CitationBuilder
from app.application.ai.services.context_assembler import ContextAssembler
from app.application.ai.services.default_prompt_builder import (
    DefaultPromptBuilder,
)
from app.application.knowledge.contracts.chunk_metadata import ChunkMetadata
from app.application.knowledge.contracts.retrieved_chunk import RetrievedChunk
from app.domain.ai.models.chat_message import ChatMessage
from app.domain.conversation.enums.message_role import MessageRole


DOCUMENT_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
OWNER_ID = UUID("11111111-1111-1111-1111-111111111111")


def chunk(
    chunk_id: str,
    content: str,
    *,
    score: float = 1.0,
    page_number: int | None = None,
) -> RetrievedChunk:
    return RetrievedChunk(
        content=content,
        metadata=ChunkMetadata(
            document_id=DOCUMENT_ID,
            filename="test.txt",
            chunk_id=chunk_id,
            chunk_index=0,
            page_number=page_number,
            owner_id=OWNER_ID,
        ),
        score=score,
    )


def test_assemble_returns_empty_context_for_no_chunks():
    assert ContextAssembler(max_tokens=10).assemble([]) == []


def test_assemble_keeps_one_chunk_and_its_metadata():
    retrieved = chunk("one", "one two", score=0.9, page_number=3)

    selected = ContextAssembler(max_tokens=3).assemble([retrieved])

    assert selected == [retrieved]
    assert selected[0].metadata.page_number == 3
    assert selected[0].score == 0.9


def test_assemble_preserves_rank_order_and_prefers_higher_ranked_chunks():
    ranked_chunks = [
        chunk("first", "one"),
        chunk("second", "two"),
        chunk("third", "three"),
    ]

    selected = ContextAssembler(max_tokens=4).assemble(ranked_chunks)

    assert [item.metadata.chunk_id for item in selected] == ["first", "second"]


def test_assemble_removes_duplicate_chunk_ids_using_first_ranked_chunk():
    ranked_chunks = [
        chunk("duplicate", "first version", score=0.9),
        chunk("duplicate", "second version", score=0.8),
        chunk("unique", "unique"),
    ]

    selected = ContextAssembler(max_tokens=10).assemble(ranked_chunks)

    assert [item.content for item in selected] == ["first version", "unique"]


def test_assemble_stops_without_partially_including_non_fitting_chunk():
    ranked_chunks = [
        chunk("first", "one"),
        chunk("does-not-fit", "two three"),
        chunk("later", "four"),
    ]

    selected = ContextAssembler(max_tokens=3).assemble(ranked_chunks)

    assert [item.metadata.chunk_id for item in selected] == ["first"]


def test_citations_are_built_only_from_selected_chunks():
    selected = ContextAssembler(max_tokens=2).assemble(
        [
            chunk("included", "one"),
            chunk("excluded", "two"),
        ]
    )

    citations = CitationBuilder.build(selected)

    assert [citation.chunk_id for citation in citations] == ["included"]


def test_prompt_builder_remains_compatible_with_selected_chunks():
    selected = [chunk("included", "selected knowledge")]

    chat_request = asyncio.run(
        DefaultPromptBuilder().build(
            PromptContext(
                messages=[
                    ChatMessage(
                        role=MessageRole.USER,
                        content="What is selected?",
                    )
                ],
                user_prompt="What is selected?",
                retrieved_chunks=selected,
            )
        )
    )

    assert "selected knowledge" in chat_request.messages[1].content
    assert chat_request.messages[-1].content == "CURRENT QUESTION\nWhat is selected?"


def test_assemble_rejects_a_negative_budget():
    with pytest.raises(ValueError, match="must not be negative"):
        ContextAssembler(max_tokens=-1)