from app.domain.knowledge.entities.document import Document
from app.domain.knowledge.enums.document_status import DocumentStatus
from app.infrastructure.knowledge.models.document_model import (
    DocumentModel,
)


def to_domain(
    model: DocumentModel,
) -> Document:
    """
    Maps a SQLAlchemy DocumentModel to a domain Document.
    """

    return Document(
        id=model.id,
        owner_id=model.owner_id,
        original_filename=model.original_filename,
        content_type=model.content_type,
        size_bytes=model.size_bytes,
        storage_key=model.storage_key,
        status=DocumentStatus(model.status),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def to_model(
    entity: Document,
) -> DocumentModel:
    """
    Maps a domain Document to a SQLAlchemy DocumentModel.
    """

    return DocumentModel(
        id=entity.id,
        owner_id=entity.owner_id,
        original_filename=entity.original_filename,
        content_type=entity.content_type,
        size_bytes=entity.size_bytes,
        storage_key=entity.storage_key,
        status=entity.status.value,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )