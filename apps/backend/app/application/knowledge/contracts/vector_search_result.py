from dataclasses import dataclass

from app.application.knowledge.contracts.retrieved_chunk import (
    RetrievedChunk,
)


@dataclass(frozen=True)
class VectorSearchResult:
    """
    Result returned from a retrieval store.
    """

    chunks: list[RetrievedChunk]
