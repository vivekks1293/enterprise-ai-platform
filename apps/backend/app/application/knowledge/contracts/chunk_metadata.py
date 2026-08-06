from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ChunkMetadata:
    """
    Metadata describing the origin of a document chunk.
    """

    document_id: UUID

    owner_id: UUID

    filename: str

    chunk_index: int

    page_number: int | None = None