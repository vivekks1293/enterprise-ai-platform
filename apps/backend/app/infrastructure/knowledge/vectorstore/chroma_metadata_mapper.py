from app.application.knowledge.contracts.chunk_metadata import (
    ChunkMetadata,
)


class ChromaMetadataMapper:
    """
    Converts application metadata into the
    metadata format required by ChromaDB.
    """

    @staticmethod
    def to_chroma(
        metadata: ChunkMetadata,
    ) -> dict[str, str | int | float | bool]:

        result: dict[str, str | int | float | bool] = {
            "document_id": str(metadata.document_id),
            "owner_id": str(metadata.owner_id),
            "filename": metadata.filename,
            "chunk_index": metadata.chunk_index,
        }

        if metadata.page_number is not None:
            result["page_number"] = metadata.page_number

        return result