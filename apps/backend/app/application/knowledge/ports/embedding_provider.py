from abc import ABC, abstractmethod

from app.application.knowledge.contracts.document_chunk import (
    DocumentChunk,
)

from app.application.knowledge.contracts.embedded_document_chunk import (
    EmbeddedDocumentChunk,
)

from app.application.knowledge.contracts.embedding_vector import (
    EmbeddingVector,
)


class EmbeddingProvider(ABC):

    @abstractmethod
    async def embed(
        self,
        chunks: list[DocumentChunk],
    ) -> list[EmbeddedDocumentChunk]:
        raise NotImplementedError

    @abstractmethod
    async def embed_query(
        self,
        query: str,
    ) -> EmbeddingVector:
        """
        Generates an embedding for a user query.
        """
        raise NotImplementedError

    