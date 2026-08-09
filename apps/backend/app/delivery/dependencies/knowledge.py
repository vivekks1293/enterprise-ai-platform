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

from app.application.knowledge.dto.index_document import (
    IndexDocumentRequest,
    IndexDocumentResponse,
)
from app.application.knowledge.use_cases.index_document import (
    IndexDocumentUseCase,
)
from app.application.knowledge.services.document_indexing_service import (
    DocumentIndexingService,
)
from app.application.common.ports.unit_of_work import UnitOfWork

from app.application.knowledge.services.document_indexing_service import (
    DocumentIndexingService,
)
from app.application.knowledge.services.document_ingestion_service import (
    DocumentIngestionService,
)
from app.application.knowledge.ports.document_chunker import (
    DocumentChunker,
)
from app.application.knowledge.ports.embedding_provider import (
    EmbeddingProvider,
)
from app.application.knowledge.ports.vector_store import (
    VectorStore,
)

from app.application.knowledge.services.document_ingestion_service import (
    DocumentIngestionService,
)

from app.core.dependencies.knowledge import (
    get_document_chunker,
    get_embedding_provider,
    get_vector_store,
)

def get_document_ingestion_service(
    file_storage: FileStorage = Depends(get_file_storage),
    parser_resolver: DocumentParserResolver = Depends(
        get_document_parser_resolver,
    ),
) -> DocumentIngestionService:
    return DocumentIngestionService(
        file_storage=file_storage,
        document_type_resolver=DocumentTypeResolver(),
        parser_resolver=parser_resolver,
    )

def get_document_indexing_service(
    ingestion_service: DocumentIngestionService = Depends(
        get_document_ingestion_service,
    ),
    chunker: DocumentChunker = Depends(
        get_document_chunker,
    ),
    embedding_provider: EmbeddingProvider = Depends(
        get_embedding_provider,
    ),
    vector_store: VectorStore = Depends(
        get_vector_store,
    ),
    document_repository: DocumentRepository = Depends(
        get_document_repository,
    ),
    unit_of_work: UnitOfWork = Depends(
        get_unit_of_work,
    ),
) -> DocumentIndexingService:

    return DocumentIndexingService(
        ingestion_service=ingestion_service,
        chunker=chunker,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        document_repository=document_repository,
        unit_of_work=unit_of_work,
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
    document_indexing_service: DocumentIndexingService = Depends(
        get_document_indexing_service,
    )
) -> UploadDocumentUseCase:
    """
    Provides the UploadDocumentUseCase with its dependencies.
    """

    return UploadDocumentUseCase(
        document_repository=document_repository,
        file_storage=file_storage,
        unit_of_work=unit_of_work,
        document_indexing_service=document_indexing_service,
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

def get_document_ingestion_service(
    file_storage: FileStorage = Depends(
        get_file_storage,
    ),
    document_parser_resolver: DocumentParserResolver = Depends(
        get_document_parser_resolver,
    ),
) -> DocumentIngestionService:

    return DocumentIngestionService(
        file_storage=file_storage,
        document_type_resolver=DocumentTypeResolver(),
        parser_resolver=document_parser_resolver,
    )

def get_document_indexing_service(
    ingestion_service: DocumentIngestionService = Depends(
        get_document_ingestion_service,
    ),
    chunker: DocumentChunker = Depends(
        get_document_chunker,
    ),
    embedding_provider: EmbeddingProvider = Depends(
        get_embedding_provider,
    ),
    vector_store: VectorStore = Depends(
        get_vector_store,
    ),
) -> DocumentIndexingService:
    """
    Provides the DocumentIndexingService.
    """

    return DocumentIndexingService(
        ingestion_service=ingestion_service,
        chunker=chunker,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )


def get_index_document_use_case(
    document_repository: DocumentRepository = Depends(
        get_document_repository,
    ),
    indexing_service: DocumentIndexingService = Depends(
        get_document_indexing_service,
    ),
    unit_of_work: UnitOfWork = Depends(
        get_unit_of_work,
    ),
) -> IndexDocumentUseCase:
    """
    Provides the IndexDocumentUseCase.
    """

    return IndexDocumentUseCase(
        document_repository=document_repository,
        indexing_service=indexing_service,
        unit_of_work=unit_of_work,
    )




#715b2f68-976a-4ff6-8439-364514e4932c
