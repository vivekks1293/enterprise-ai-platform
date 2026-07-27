from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.knowledge.entities.document import Document
from app.domain.knowledge.repositories.document_repository import (
    DocumentRepository,
)
from app.infrastructure.knowledge.mappers.document_mapper import (
    to_domain,
    to_model,
)
from app.infrastructure.knowledge.models.document_model import (
    DocumentModel,
)


class PostgresDocumentRepository(DocumentRepository):
    """
    PostgreSQL implementation of DocumentRepository.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def create(
        self,
        document: Document,
    ) -> None:
        self._session.add(
            to_model(document)
        )

    async def get_by_id(
        self,
        document_id: UUID,
        owner_id: UUID,
    ) -> Document | None:

        result = await self._session.execute(
            select(DocumentModel).where(
                DocumentModel.id == document_id,
                DocumentModel.owner_id == owner_id,
            )
        )

        model = result.scalar_one_or_none()

        if model is None:
            return None

        return to_domain(model)

    async def list_by_owner(
        self,
        owner_id: UUID,
    ) -> list[Document]:

        result = await self._session.execute(
            select(DocumentModel)
            .where(
                DocumentModel.owner_id == owner_id
            )
            .order_by(
                DocumentModel.created_at.desc()
            )
        )

        return [
            to_domain(model)
            for model in result.scalars().all()
        ]

    async def update(
        self,
        document: Document,
    ) -> None:

        result = await self._session.execute(
            select(DocumentModel).where(
                DocumentModel.id == document.id,
                DocumentModel.owner_id == document.owner_id,
            )
        )

        model = result.scalar_one_or_none()

        if model is None:
            return

        model.original_filename = document.original_filename
        model.content_type = document.content_type
        model.size_bytes = document.size_bytes
        model.storage_key = document.storage_key
        model.status = document.status.value
        model.updated_at = document.updated_at

    async def delete(
        self,
        document_id: UUID,
        owner_id: UUID,
    ) -> None:

        result = await self._session.execute(
            select(DocumentModel).where(
                DocumentModel.id == document_id,
                DocumentModel.owner_id == owner_id,
            )
        )

        model = result.scalar_one_or_none()

        if model is not None:
            await self._session.delete(model)