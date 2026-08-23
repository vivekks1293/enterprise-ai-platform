import asyncio
from uuid import UUID

from app.application.ai.dto.prompt_context import PromptContext
from app.application.ai.services.default_prompt_builder import (
    DefaultPromptBuilder,
)
from app.application.knowledge.contracts.chunk_metadata import ChunkMetadata
from app.application.knowledge.contracts.retrieved_chunk import RetrievedChunk
from app.domain.ai.models.chat_message import ChatMessage
from app.domain.conversation.enums.message_role import MessageRole


DOCUMENT_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
OWNER_ID = UUID("11111111-1111-1111-1111-111111111111")


def retrieved_chunk() -> RetrievedChunk:
    return RetrievedChunk(
        content="The approval period is five business days.",
        metadata=ChunkMetadata(
            document_id=DOCUMENT_ID,
            filename="approval-policy.pdf",
            chunk_id="approval-period",
            chunk_index=4,
            page_number=12,
            owner_id=OWNER_ID,
        ),
        score=0.91,
    )


def build_request(
    *,
    messages: list[ChatMessage],
    chunks: list[RetrievedChunk],
):
    return asyncio.run(
        DefaultPromptBuilder().build(
            PromptContext(
                messages=messages,
                user_prompt="How long does approval take?",
                retrieved_chunks=chunks,
            )
        )
    )


def test_build_creates_structured_provider_agnostic_prompt():
    request = build_request(
        messages=[
            ChatMessage(
                role=MessageRole.USER,
                content="Tell me about approval.",
            ),
            ChatMessage(
                role=MessageRole.ASSISTANT,
                content="What part of approval?",
            ),
            ChatMessage(
                role=MessageRole.USER,
                content="How long does approval take?",
            ),
        ],
        chunks=[retrieved_chunk()],
    )

    system_instructions, retrieved_knowledge, *history, question = request.messages

    assert system_instructions.role == MessageRole.SYSTEM
    assert "GROUNDING RULES" in system_instructions.content
    assert "enterprise knowledge is authoritative" in system_instructions.content
    assert "partially answers a question" in system_instructions.content
    assert "Do not claim that information exists" in system_instructions.content
    assert retrieved_knowledge.role == MessageRole.SYSTEM
    assert "RETRIEVED KNOWLEDGE" in retrieved_knowledge.content
    assert "[Source 1]" in retrieved_knowledge.content
    assert "Document ID: aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa" in retrieved_knowledge.content
    assert "Chunk ID: approval-period" in retrieved_knowledge.content
    assert "Filename: approval-policy.pdf" in retrieved_knowledge.content
    assert "Page: 12" in retrieved_knowledge.content
    assert "Score: 0.91" in retrieved_knowledge.content
    assert "The approval period is five business days." in retrieved_knowledge.content
    assert history == [
        ChatMessage(
            role=MessageRole.USER,
            content="Tell me about approval.",
        ),
        ChatMessage(
            role=MessageRole.ASSISTANT,
            content="What part of approval?",
        ),
    ]
    assert question.role == MessageRole.USER
    assert question.content == "CURRENT QUESTION\nHow long does approval take?"
    assert sum(
        "How long does approval take?" in message.content
        for message in request.messages
    ) == 1
    assert request.stream is True


def test_build_handles_empty_retrieved_knowledge():
    request = build_request(
        messages=[
            ChatMessage(
                role=MessageRole.USER,
                content="How long does approval take?",
            )
        ],
        chunks=[],
    )

    assert request.messages[1].content == (
        "RETRIEVED KNOWLEDGE (UNTRUSTED REFERENCE DATA)\n"
        "No retrieved knowledge is available."
    )
    assert request.messages[-1].content == (
        "CURRENT QUESTION\nHow long does approval take?"
    )