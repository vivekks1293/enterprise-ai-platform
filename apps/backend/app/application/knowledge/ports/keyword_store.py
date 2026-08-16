from abc import ABC, abstractmethod

from app.application.knowledge.contracts.document_chunk import DocumentChunk
from app.application.knowledge.contracts.vector_search_filter import VectorSearchFilter
from app.application.knowledge.contracts.vector_search_result import VectorSearchResult


class KeywordStore(ABC):
    """Stores document chunks for lexical retrieval."""

    @abstractmethod
    async def add(self, chunks: list[DocumentChunk]) -> None:
        """Adds or updates chunks in the lexical corpus."""

    @abstractmethod
    async def search(
        self,
        *,
        query: str,
        filter: VectorSearchFilter,
        top_k: int,
    ) -> VectorSearchResult:
        """Searches the lexical corpus using the raw query text."""
