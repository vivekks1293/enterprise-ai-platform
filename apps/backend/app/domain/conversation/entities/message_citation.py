from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class MessageCitation:
    """
    Represents one citation attached to
    an assistant message.
    """

    id: UUID

    message_id: UUID

    document_id: UUID

    filename: str

    chunk_id: str

    chunk_index: int

    page_number: int | None

    similarity_score: float