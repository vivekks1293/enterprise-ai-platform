from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Citation:
    """
    Value object representing evidence supporting an assistant message.
    """

    document_id: UUID

    chunk_id: str

    chunk_index: int

    page_number: int | None

    similarity_score: float