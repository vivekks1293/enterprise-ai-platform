from dataclasses import dataclass

from app.application.knowledge.contracts.chunk_metadata import (
    ChunkMetadata,
)


@dataclass(frozen=True)
class RetrievedChunk:
    """
    Represents one chunk retrieved from the vector store.
    """

    content: str

    metadata: ChunkMetadata

    distance: float