from abc import ABC, abstractmethod

from app.domain.knowledge.entities.document import Document
from app.application.knowledge.contracts.parsed_document import (
    ParsedDocument,
)
from app.application.knowledge.contracts.document_chunk import (
    DocumentChunk,
)


class DocumentChunker(ABC):

    @abstractmethod
    async def chunk(
        self,
        *,
        document: Document,
        parsed_document: ParsedDocument,
    ) -> list[DocumentChunk]:
        raise NotImplementedError