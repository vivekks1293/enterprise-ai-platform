from app.application.common.ports.unit_of_work import UnitOfWork
from app.application.knowledge.dto.index_document import (
    IndexDocumentRequest,
    IndexDocumentResponse,
)
from app.application.knowledge.exceptions import (
    DocumentNotFoundError,
)
from app.application.knowledge.services.document_indexing_service import (
    DocumentIndexingService,
)
from app.domain.knowledge.repositories.document_repository import (
    DocumentRepository,
)


class IndexDocumentUseCase:
    """
    Orchestrates the document indexing workflow.

    Responsibilities:
    - Validate document ownership
    - Update document lifecycle
    - Delegate indexing to DocumentIndexingService
    """

    def __init__(
        self,
        document_repository: DocumentRepository,
        indexing_service: DocumentIndexingService,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._document_repository = document_repository
        self._indexing_service = indexing_service
        self._unit_of_work = unit_of_work

    async def execute(
        self,
        request: IndexDocumentRequest,
    ) -> IndexDocumentResponse:

        # --------------------------------------------------
        # 1. Load document
        # --------------------------------------------------

        document = await self._document_repository.get_by_id(
            document_id=request.document_id,
            owner_id=request.owner_id,
        )

        if document is None:
            raise DocumentNotFoundError()

        # --------------------------------------------------
        # 2. Mark indexing started
        # --------------------------------------------------

        document.mark_indexing()

        await self._document_repository.update(document)
        await self._unit_of_work.commit()

        try:

            # --------------------------------------------------
            # 3. Execute indexing pipeline
            # --------------------------------------------------

            chunk_count = await self._indexing_service.index(
                document,
            )

            # --------------------------------------------------
            # 4. Mark indexed
            # --------------------------------------------------

            document.mark_indexed()

            await self._document_repository.update(document)
            await self._unit_of_work.commit()

            # --------------------------------------------------
            # 5. Return response
            # --------------------------------------------------

            return IndexDocumentResponse(
                document_id=document.id,
                status=document.status.value,
                chunk_count=chunk_count,
            )

        except Exception:

            # --------------------------------------------------
            # 6. Mark failed
            # --------------------------------------------------

            document.mark_failed()

            await self._document_repository.update(document)
            await self._unit_of_work.commit()

            raise