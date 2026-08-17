from abc import ABC, abstractmethod

from app.application.knowledge.contracts.retrieved_chunk import (
    RetrievedChunk,
)
from app.application.knowledge.contracts.vector_search_result import (
    VectorSearchResult,
)


class Reranker(ABC):
    """Reorders retrieved chunks to improve final context quality."""

    @abstractmethod
    def rerank(
        self,
        *,
        query: str,
        chunks: list[RetrievedChunk],
        top_k: int,
    ) -> VectorSearchResult:
        raise NotImplementedError
