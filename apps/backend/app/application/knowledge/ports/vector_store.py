from abc import ABC, abstractmethod

from app.application.knowledge.contracts.embedded_document_chunk import (
    EmbeddedDocumentChunk,
)


class VectorStore(ABC):

    @abstractmethod
    async def add(
        self,
        chunks: list[EmbeddedDocumentChunk],
    ) -> None:
        raise NotImplementedError