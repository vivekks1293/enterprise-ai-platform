from app.application.common.ports.unit_of_work import UnitOfWork
from app.application.knowledge.dto.delete_document import (
    DeleteDocumentRequest,
)
from app.application.knowledge.exceptions import (
    DocumentNotFoundError,
)
from app.application.knowledge.ports.file_storage import (
    FileStorage,
)
from app.domain.knowledge.repositories.document_repository import (
    DocumentRepository,
)


class DeleteDocumentUseCase:
    """
    Deletes a knowledge document owned by the authenticated user.
    """

    def __init__(
        self,
        document_repository: DocumentRepository,
        file_storage: FileStorage,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._document_repository = document_repository
        self._file_storage = file_storage
        self._unit_of_work = unit_of_work

    async def execute(
        self,
        request: DeleteDocumentRequest,
    ) -> None:

        # 1. Validate document ownership.
        document = await self._document_repository.get_by_id(
            document_id=request.document_id,
            owner_id=request.owner_id,
        )

        if document is None:
            raise DocumentNotFoundError()

        # 2. Delete physical file first.
        await self._file_storage.delete(
            storage_key=document.storage_key,
        )

        # 3. Delete document metadata.
        await self._document_repository.delete(
            document_id=request.document_id,
            owner_id=request.owner_id,
        )

        # 4. Commit database transaction.
        await self._unit_of_work.commit()