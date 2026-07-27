from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.knowledge.entities.document import Document


class DocumentRepository(ABC):
    """
    Persistence contract for knowledge documents.
    """

    @abstractmethod
    async def create(
        self,
        document: Document,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(
        self,
        document_id: UUID,
        owner_id: UUID,
    ) -> Document | None:
        raise NotImplementedError

    @abstractmethod
    async def list_by_owner(
        self,
        owner_id: UUID,
    ) -> list[Document]:
        raise NotImplementedError

    @abstractmethod
    async def update(
        self,
        document: Document,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(
        self,
        document_id: UUID,
        owner_id: UUID,
    ) -> None:
        raise NotImplementedError