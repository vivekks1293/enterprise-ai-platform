from uuid import UUID

from app.application.knowledge.contracts.chunk_metadata import (
    ChunkMetadata,
)


class ChromaMetadataMapper:
    """
    Maps application ChunkMetadata to and from
    ChromaDB metadata.
    """

    @staticmethod
    def to_chroma(
        metadata: ChunkMetadata,
    ) -> dict:
        """
        Converts domain/application metadata into
        ChromaDB-compatible metadata.
        """

        return {
            "document_id": str(metadata.document_id),
            "owner_id": str(metadata.owner_id),
            "filename": metadata.filename,
            "chunk_id": metadata.chunk_id,
            "chunk_index": metadata.chunk_index,
            "page_number": metadata.page_number,
        }

    @staticmethod
    def from_chroma(
        metadata: dict,
    ) -> ChunkMetadata:
        """
        Converts ChromaDB metadata back into
        application ChunkMetadata.
        """

        return ChunkMetadata(
            document_id=UUID(metadata["document_id"]),
            owner_id=UUID(metadata["owner_id"]),
            filename=metadata["filename"],
            chunk_id=metadata["chunk_id"],
            chunk_index=int(metadata["chunk_index"]),
            page_number=metadata.get("page_number"),
        )