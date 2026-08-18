from dataclasses import dataclass

from app.application.knowledge.contracts.retrieved_chunk import RetrievedChunk
from app.domain.ai.models.citation import Citation


@dataclass(frozen=True)
class GenerationEvaluationRecord:
    """Completed application-level data for generation evaluation."""

    question: str

    answer: str

    selected_chunks: list[RetrievedChunk]

    citations: list[Citation]