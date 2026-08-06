from langchain_chroma import Chroma

from app.application.knowledge.contracts.embedded_document_chunk import (
    EmbeddedDocumentChunk,
)
from app.application.knowledge.ports.vector_store import (
    VectorStore,
)
from app.infrastructure.knowledge.vectorstore.chroma_metadata_mapper import (
    ChromaMetadataMapper,
)


class ChromaVectorStore(VectorStore):
    """
    Stores embedded document chunks in ChromaDB.
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

        if not chunks:
            return

        ids: list[str] = []
        documents: list[str] = []
        embeddings: list[list[float]] = []
        metadatas: list[dict] = []

        for item in chunks:

            ids.append(
                f"{item.chunk.metadata.document_id}_{item.chunk.metadata.chunk_index}"
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