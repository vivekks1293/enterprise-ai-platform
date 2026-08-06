from dataclasses import dataclass
from typing import Any
from uuid import UUID
from app.application.knowledge.contracts.chunk_metadata import (
    ChunkMetadata,
)


@dataclass(frozen=True)
class DocumentChunk:
    """
    Represents one searchable chunk extracted
    from a parsed document.
    """

    content: str

    metadata: ChunkMetadata