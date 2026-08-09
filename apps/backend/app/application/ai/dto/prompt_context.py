from dataclasses import dataclass

from app.application.knowledge.contracts.retrieved_chunk import (
    RetrievedChunk,
)
from app.domain.ai.models.chat_message import ChatMessage


@dataclass(frozen=True)
class PromptContext:
    """
    Represents everything required to construct
    the final prompt sent to the LLM.
    """

    messages: list[ChatMessage]

    retrieved_chunks: list[RetrievedChunk]

    user_prompt: str