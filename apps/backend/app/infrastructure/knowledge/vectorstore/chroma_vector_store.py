from uuid import UUID

from langchain_chroma import Chroma

from app.application.knowledge.contracts.embedding_vector import (
    EmbeddingVector,
)
from app.application.knowledge.contracts.embedded_document_chunk import (
    EmbeddedDocumentChunk,
)
from app.application.knowledge.contracts.retrieved_chunk import (
    RetrievedChunk,
)
from app.application.knowledge.contracts.vector_search_filter import (
    VectorSearchFilter,
)
from app.application.knowledge.contracts.vector_search_result import (
    VectorSearchResult,
)
from app.application.knowledge.ports.vector_store import (
    VectorStore,
)
from app.infrastructure.knowledge.vectorstore.chroma_metadata_mapper import (
    ChromaMetadataMapper,
)


class ChromaVectorStore(VectorStore):
    """
    Stores and retrieves embedded document chunks
    using ChromaDB.
    """

    def __init__(
        self,
        collection: Chroma,
    ) -> None:
        self._collection = collection

    async def add(
        self,
        chunks: list[EmbeddedDocumentChunk],
    ) -> None:
        """
        Adds embedded document chunks to ChromaDB.
        """

        if not chunks:
            return

        ids: list[str] = []
        documents: list[str] = []
        embeddings: list[list[float]] = []
        metadatas: list[dict] = []

        for item in chunks:

            ids.append(
                f"{item.chunk.metadata.document_id}_"
                f"{item.chunk.metadata.chunk_id}"
            )

            documents.append(
                item.chunk.content
            )

            embeddings.append(
                item.embedding.values
            )

            metadatas.append(
                ChromaMetadataMapper.to_chroma(
                    item.chunk.metadata
                )
            )

        self._collection._collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    async def search(
        self,
        *,
        embedding: EmbeddingVector,
        filter: VectorSearchFilter,
        top_k: int,
    ) -> VectorSearchResult:
        """
        Searches ChromaDB for semantically similar chunks.
        """

        result = self._collection._collection.query(
            query_embeddings=[embedding.values],
            n_results=top_k,
            where={
                "owner_id": str(filter.owner_id),
            },
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

        chunks: list[RetrievedChunk] = []

        documents = result["documents"][0]
        metadatas = result["metadatas"][0]
        distances = result["distances"][0]

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
            strict=True,
        ):
            chunk_metadata = ChromaMetadataMapper.from_chroma(
                metadata,
            )

            chunks.append(
                RetrievedChunk(
                    content=document,
                    metadata=chunk_metadata,
                    similarity_score=1 - distance,
                )
            )

        return VectorSearchResult(
            chunks=chunks,
        )