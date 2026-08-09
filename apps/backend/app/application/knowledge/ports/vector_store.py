from abc import ABC, abstractmethod

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
    async def search(
        self,
        *,
        embedding: EmbeddingVector,
        filter: VectorSearchFilter,
        top_k: int,
    ) -> VectorSearchResult:
        raise NotImplementedError