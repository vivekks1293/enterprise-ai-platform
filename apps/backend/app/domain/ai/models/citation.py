from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True, frozen=True)
class Citation:
    """
    Represents a source reference associated with an AI response.
    """

    citation_id: int

    document_id: UUID

    chunk_id: str

    filename: str

    page_number: int | None

    similarity_score: float