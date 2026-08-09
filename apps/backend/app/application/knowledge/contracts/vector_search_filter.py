from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class VectorSearchFilter:
    """
    Restricts vector search.
    """

    owner_id: UUID

    document_id: UUID | None = None