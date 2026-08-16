from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalEvaluationCase:
    """
    Represents one retrieval evaluation question
    and its expected relevant chunks.
    """

    id: str

    question: str

    relevant_chunk_ids: set[str]