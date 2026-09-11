from abc import ABC, abstractmethod
from uuid import UUID

from app.application.knowledge.contracts.embedded_document_chunk import (
    EmbeddedDocumentChunk,
)

from app.application.knowledge.contracts.embedding_vector import (
    EmbeddingVector,
)
from app.application.knowledge.contracts.vector_search_filter import (
    VectorSearchFilter,
)
from app.application.knowledge.contracts.vector_search_result import (
    VectorSearchResult,
)



class VectorStore(ABC):

    @abstractmethod
    async def add(
        self,
        chunks: list[EmbeddedDocumentChunk],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(
        self,
        document_id: UUID,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def search(
        self,
        *,
        embedding: EmbeddingVector,
        filter: VectorSearchFilter,
        top_k: int,
    ) -> VectorSearchResult:
        raise NotImplementedError