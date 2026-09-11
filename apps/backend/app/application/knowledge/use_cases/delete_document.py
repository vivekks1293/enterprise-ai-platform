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
from app.application.knowledge.ports.keyword_store import (
    KeywordStore,
)
from app.application.knowledge.ports.vector_store import (
    VectorStore,
)
from app.domain.knowledge.repositories.document_repository import (
    DocumentRepository,
)


class DeleteDocumentUseCase:
    """
    Deletes a knowledge document owned by the authenticated user,
    including its vector embeddings, keyword index chunks, physical file,
    and database record.
    """

    def __init__(
        self,
        document_repository: DocumentRepository,
        file_storage: FileStorage,
        vector_store: VectorStore,
        keyword_store: KeywordStore,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._document_repository = document_repository
        self._file_storage = file_storage
        self._vector_store = vector_store
        self._keyword_store = keyword_store
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

        # 2. Delete vector embeddings from vector store.
        await self._vector_store.delete(
            document_id=request.document_id,
        )

        # 3. Delete lexical chunks from keyword store.
        await self._keyword_store.delete(
            document_id=request.document_id,
        )

        # 4. Delete physical file.
        await self._file_storage.delete(
            storage_key=document.storage_key,
        )

        # 5. Delete document metadata.
        await self._document_repository.delete(
            document_id=request.document_id,
            owner_id=request.owner_id,
        )

        # 6. Commit database transaction.
        await self._unit_of_work.commit()