from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True, frozen=True)
class Citation:
    """
    Represents one citation supporting an AI response.
    """

    document_id: UUID

    filename: str

    chunk_id: str

    chunk_index: int

    page_number: int | None

    similarity_score: float