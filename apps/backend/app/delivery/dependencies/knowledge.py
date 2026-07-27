from fastapi import Depends

from app.application.common.ports.unit_of_work import UnitOfWork
from app.application.knowledge.ports.file_storage import FileStorage
from app.application.knowledge.use_cases.list_documents import (
    ListDocumentsUseCase,
)
from app.application.knowledge.use_cases.upload_document import (
    UploadDocumentUseCase,
)
from app.core.dependencies.common import get_unit_of_work
from app.core.dependencies.knowledge import (
    get_document_repository,
    get_file_storage,
)
from app.domain.knowledge.repositories.document_repository import (
    DocumentRepository,
)

from app.application.knowledge.use_cases.get_document import (
    GetDocumentUseCase,
)

from app.application.knowledge.use_cases.download_document import (
    DownloadDocumentUseCase,
)
from app.application.knowledge.use_cases.delete_document import (
    DeleteDocumentUseCase,
)

from app.application.knowledge.services.document_type_resolver import (
    DocumentTypeResolver,
)
from app.application.knowledge.use_cases.ingest_document import (
    IngestDocumentUseCase,
)
from app.application.knowledge.ports.document_parser_resolver import (
    DocumentParserResolver,
)
from app.core.dependencies.knowledge import (
    get_document_parser_resolver,
    get_document_repository,
    get_file_storage,
)

from app.application.knowledge.ports.document_parser_resolver import (
    DocumentParserResolver,
)
from app.application.knowledge.services.document_type_resolver import (
    DocumentTypeResolver,
)
from app.application.knowledge.use_cases.ingest_document import (
    IngestDocumentUseCase,
)

def get_upload_document_use_case(
    document_repository: DocumentRepository = Depends(
        get_document_repository
    ),
    file_storage: FileStorage = Depends(
        get_file_storage
    ),
    unit_of_work: UnitOfWork = Depends(
        get_unit_of_work
    ),
) -> UploadDocumentUseCase:
    """
    Provides the UploadDocumentUseCase with its dependencies.
    """

    return UploadDocumentUseCase(
        document_repository=document_repository,
        file_storage=file_storage,
        unit_of_work=unit_of_work,
    )


def get_list_documents_use_case(
    document_repository: DocumentRepository = Depends(
        get_document_repository
    ),
) -> ListDocumentsUseCase:
    """
    Provides the ListDocumentsUseCase with its dependencies.
    """

    return ListDocumentsUseCase(
        document_repository=document_repository,
    )

def get_get_document_use_case(
    document_repository: DocumentRepository = Depends(
        get_document_repository
    ),
) -> GetDocumentUseCase:
    """
    Provides the GetDocumentUseCase.
    """

    return GetDocumentUseCase(
        document_repository=document_repository,
    )

def get_download_document_use_case(
    document_repository: DocumentRepository = Depends(
        get_document_repository
    ),
    file_storage: FileStorage = Depends(
        get_file_storage
    ),
) -> DownloadDocumentUseCase:
    """
    Provides the DownloadDocumentUseCase.
    """

    return DownloadDocumentUseCase(
        document_repository=document_repository,
        file_storage=file_storage,
    )

def get_delete_document_use_case(
    document_repository: DocumentRepository = Depends(
        get_document_repository
    ),
    file_storage: FileStorage = Depends(
        get_file_storage
    ),
    unit_of_work: UnitOfWork = Depends(
        get_unit_of_work
    ),
) -> DeleteDocumentUseCase:
    """
    Provides the DeleteDocumentUseCase.
    """

    return DeleteDocumentUseCase(
        document_repository=document_repository,
        file_storage=file_storage,
        unit_of_work=unit_of_work,
    )


def get_ingest_document_use_case(
    document_repository: DocumentRepository = Depends(
        get_document_repository
    ),
    file_storage: FileStorage = Depends(
        get_file_storage
    ),
    document_parser_resolver: DocumentParserResolver = Depends(
        get_document_parser_resolver
    ),
    unit_of_work: UnitOfWork = Depends(
        get_unit_of_work
    ),
) -> IngestDocumentUseCase:

    return IngestDocumentUseCase(
        document_repository=document_repository,
        file_storage=file_storage,
        document_type_resolver=DocumentTypeResolver(),
        document_parser_resolver=document_parser_resolver,
        unit_of_work=unit_of_work,
    )

def get_ingest_document_use_case(
    document_repository: DocumentRepository = Depends(
        get_document_repository
    ),
    file_storage: FileStorage = Depends(
        get_file_storage
    ),
    document_parser_resolver: DocumentParserResolver = Depends(
        get_document_parser_resolver
    ),
    unit_of_work: UnitOfWork = Depends(
        get_unit_of_work
    ),
) -> IngestDocumentUseCase:

    return IngestDocumentUseCase(
        document_repository=document_repository,
        file_storage=file_storage,
        document_type_resolver=DocumentTypeResolver(),
        document_parser_resolver=document_parser_resolver,
        unit_of_work=unit_of_work,
    )