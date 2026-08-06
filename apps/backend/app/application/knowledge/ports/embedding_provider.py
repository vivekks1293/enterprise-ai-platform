from abc import ABC, abstractmethod

from app.application.knowledge.contracts.document_chunk import (
    DocumentChunk,
)

from app.application.knowledge.contracts.embedded_document_chunk import (
    EmbeddedDocumentChunk,
)


class EmbeddingProvider(ABC):

    @abstractmethod
    async def embed(
        self,
        chunks: list[DocumentChunk],
    ) -> list[EmbeddedDocumentChunk]:
        raise NotImplementedError