from app.application.knowledge.services.document_ingestion_service import (
    DocumentIngestionService,
)
from app.application.knowledge.ports.document_chunker import (
    DocumentChunker,
)
from app.application.knowledge.ports.embedding_provider import (
    EmbeddingProvider,
)
from app.application.knowledge.ports.vector_store import (
    VectorStore,
)
from app.domain.knowledge.entities.document import Document


class DocumentIndexingService:
    """
    Converts a stored document into searchable vectors.
    """

    def __init__(
        self,
        ingestion_service: DocumentIngestionService,
        chunker: DocumentChunker,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
    ) -> None:

        self._ingestion_service = ingestion_service
        self._chunker = chunker
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store

    async def index(
        self,
        document: Document,
    ) -> int:
        """
        Indexes a document into the configured vector store.

        Returns
        -------
        int
            Number of chunks indexed.
        """

        parsed_document = await self._ingestion_service.ingest(
            document,
        )

        chunks = await self._chunker.chunk(
            document=document,
            parsed_document=parsed_document,
        )

        embedded_chunks = await self._embedding_provider.embed(
            chunks,
        )

        await self._vector_store.add(
            embedded_chunks,
        )

        return len(chunks)