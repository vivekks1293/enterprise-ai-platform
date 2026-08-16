from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievedEvaluationChunk:
    rank: int
    chunk_id: str
    distance: float
    filename: str
    page_number: int | None
    content: str


@dataclass(frozen=True)
class RetrievalEvaluationResult:
    case_id: str
    question: str
    retrieved_chunks: list[RetrievedEvaluationChunk]
    relevant_chunk_ids: set[str]
    precision_at_k: float
    recall_at_k: float
    reciprocal_rank: float