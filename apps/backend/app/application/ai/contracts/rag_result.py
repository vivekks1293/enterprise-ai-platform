from dataclasses import dataclass

from app.application.knowledge.contracts.retrieved_chunk import (
    RetrievedChunk,
)


@dataclass(slots=True)
class RAGResult:
    """
    Result produced by the AI runtime before persistence.
    """

    answer: str

    retrieved_chunks: list[RetrievedChunk]