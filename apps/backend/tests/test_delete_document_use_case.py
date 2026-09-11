import asyncio
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4
import pytest

from app.application.common.ports.unit_of_work import UnitOfWork
from app.application.knowledge.dto.delete_document import DeleteDocumentRequest
from app.application.knowledge.exceptions import DocumentNotFoundError
from app.application.knowledge.ports.file_storage import FileStorage
from app.application.knowledge.ports.keyword_store import KeywordStore
from app.application.knowledge.ports.vector_store import VectorStore
from app.application.knowledge.use_cases.delete_document import DeleteDocumentUseCase
from app.domain.knowledge.entities.document import Document
from app.domain.knowledge.repositories.document_repository import DocumentRepository


def test_delete_document_deletes_vectors_keywords_file_and_metadata():
    asyncio.run(_test_delete_document_deletes_vectors_keywords_file_and_metadata())


async def _test_delete_document_deletes_vectors_keywords_file_and_metadata():
    # Setup
    document_id = uuid4()
    owner_id = uuid4()
    storage_key = "storage/key/doc123.pdf"

    mock_doc = MagicMock(spec=Document)
    mock_doc.storage_key = storage_key

    repo = AsyncMock(spec=DocumentRepository)
    repo.get_by_id.return_value = mock_doc

    file_storage = AsyncMock(spec=FileStorage)
    vector_store = AsyncMock(spec=VectorStore)
    keyword_store = AsyncMock(spec=KeywordStore)
    uow = AsyncMock(spec=UnitOfWork)

    use_case = DeleteDocumentUseCase(
        document_repository=repo,
        file_storage=file_storage,
        vector_store=vector_store,
        keyword_store=keyword_store,
        unit_of_work=uow,
    )

    # Execute
    request = DeleteDocumentRequest(
        document_id=document_id,
        owner_id=owner_id,
    )
    await use_case.execute(request)

    # Verify repository get
    repo.get_by_id.assert_awaited_once_with(
        document_id=document_id,
        owner_id=owner_id,
    )

    # Verify vector store delete
    vector_store.delete.assert_awaited_once_with(
        document_id=document_id,
    )

    # Verify keyword store delete
    keyword_store.delete.assert_awaited_once_with(
        document_id=document_id,
    )

    # Verify file storage delete
    file_storage.delete.assert_awaited_once_with(
        storage_key=storage_key,
    )

    # Verify document repo delete
    repo.delete.assert_awaited_once_with(
        document_id=document_id,
        owner_id=owner_id,
    )

    # Verify transaction commit
    uow.commit.assert_awaited_once()


def test_delete_document_raises_when_not_found():
    asyncio.run(_test_delete_document_raises_when_not_found())


async def _test_delete_document_raises_when_not_found():
    document_id = uuid4()
    owner_id = uuid4()

    repo = AsyncMock(spec=DocumentRepository)
    repo.get_by_id.return_value = None

    file_storage = AsyncMock(spec=FileStorage)
    vector_store = AsyncMock(spec=VectorStore)
    keyword_store = AsyncMock(spec=KeywordStore)
    uow = AsyncMock(spec=UnitOfWork)

    use_case = DeleteDocumentUseCase(
        document_repository=repo,
        file_storage=file_storage,
        vector_store=vector_store,
        keyword_store=keyword_store,
        unit_of_work=uow,
    )

    request = DeleteDocumentRequest(
        document_id=document_id,
        owner_id=owner_id,
    )

    with pytest.raises(DocumentNotFoundError):
        await use_case.execute(request)

    # Verify none of the mutating actions were invoked
    vector_store.delete.assert_not_awaited()
    keyword_store.delete.assert_not_awaited()
    file_storage.delete.assert_not_awaited()
    repo.delete.assert_not_awaited()
    uow.commit.assert_not_awaited()

