from dataclasses import dataclass

from app.application.knowledge.contracts.chunk_metadata import (
    ChunkMetadata,
)


@dataclass(frozen=True)
class RetrievedChunk:
    """
    Represents one chunk retrieved from a retrieval store.
    """

    content: str

    metadata: ChunkMetadata

    # Higher values represent stronger relevance. Chroma distances are converted
    # to this common representation by its adapter.
    score: float
