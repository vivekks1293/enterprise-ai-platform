from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class DeleteDocumentRequest:
    owner_id: UUID
    document_id: UUID