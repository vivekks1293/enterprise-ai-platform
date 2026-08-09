from app.application.common.ports.unit_of_work import UnitOfWork
from app.application.knowledge.ports.document_chunker import (
    DocumentChunker,
)
from app.application.knowledge.ports.embedding_provider import (
    EmbeddingProvider,
)
from app.application.knowledge.ports.vector_store import (
    VectorStore,
)
from app.application.knowledge.services.document_ingestion_service import (
    DocumentIngestionService,
)
from app.domain.knowledge.entities.document import Document
from app.domain.knowledge.repositories.document_repository import (
    DocumentRepository,
)


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
        document_repository: DocumentRepository,
        unit_of_work: UnitOfWork,
    ) -> None:

        self._ingestion_service = ingestion_service
        self._chunker = chunker
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
        self._document_repository = document_repository
        self._unit_of_work = unit_of_work

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

        # ------------------------------------------
        # Mark indexing started
        # ------------------------------------------

        document.mark_indexing()

        await self._document_repository.update(document)
        await self._unit_of_work.commit()

        try:

            # ------------------------------------------
            # Ingest document
            # ------------------------------------------

            parsed_document = await self._ingestion_service.ingest(
                document,
            )

            # ------------------------------------------
            # Chunk document
            # ------------------------------------------

            chunks = await self._chunker.chunk(
                document=document,
                parsed_document=parsed_document,
            )

            # ------------------------------------------
            # Generate embeddings
            # ------------------------------------------

            embedded_chunks = await self._embedding_provider.embed(
                chunks,
            )

            # ------------------------------------------
            # Store vectors
            # ------------------------------------------

            await self._vector_store.add(
                embedded_chunks,
            )

            # ------------------------------------------
            # Mark indexing completed
            # ------------------------------------------

            document.mark_indexed()

            await self._document_repository.update(document)
            await self._unit_of_work.commit()

            return len(chunks)

        except Exception:

            # ------------------------------------------
            # Mark indexing failed
            # ------------------------------------------

            document.mark_failed()

            await self._document_repository.update(document)
            await self._unit_of_work.commit()

            raise