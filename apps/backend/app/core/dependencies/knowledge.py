from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.knowledge.ports.file_storage import FileStorage
from app.core.config.settings import settings
from app.core.dependencies.database import get_db_session
from app.domain.knowledge.repositories.document_repository import (
    DocumentRepository,
)
from app.infrastructure.knowledge.repositories.postgres_document_repository import (
    PostgresDocumentRepository,
)
from app.infrastructure.knowledge.storage.local_file_storage import (
    LocalFileStorage,
)

from app.application.knowledge.enums.document_type import (
    DocumentType,
)
from app.application.knowledge.ports.document_parser_resolver import (
    DocumentParserResolver,
)
from app.infrastructure.knowledge.parsers.default_document_parser_resolver import (
    DefaultDocumentParserResolver,
)
from app.infrastructure.knowledge.parsers.markdown_document_parser import (
    MarkdownDocumentParser,
)
from app.infrastructure.knowledge.parsers.text_document_parser import (
    TextDocumentParser,
)
from app.infrastructure.knowledge.parsers.pdf_document_parser import (
    PdfDocumentParser,
)
from app.infrastructure.knowledge.parsers.docx_document_parser import (
    DocxDocumentParser,
)

from app.application.knowledge.ports.document_chunker import (
    DocumentChunker,
)

from app.infrastructure.knowledge.chunking.langchain_document_chunker import (
    LangChainDocumentChunker,
)

from langchain_openai import (
    OpenAIEmbeddings,
)

from app.application.knowledge.ports.embedding_provider import (
    EmbeddingProvider,
)

from app.infrastructure.knowledge.embeddings.openai_embedding_provider import (
    OpenAIEmbeddingProvider,
)

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from app.application.knowledge.ports.vector_store import (
    VectorStore,
)
from app.application.knowledge.ports.keyword_store import KeywordStore

from app.infrastructure.knowledge.vectorstore.chroma_vector_store import (
    ChromaVectorStore,
)
from app.infrastructure.knowledge.keywordstore.bm25_keyword_store import (
    BM25KeywordStore,
)

from app.application.knowledge.services.document_ingestion_service import (
    DocumentIngestionService,
)
from app.application.knowledge.services.document_type_resolver import (
    DocumentTypeResolver,
)

from app.application.knowledge.services.document_indexing_service import (
    DocumentIndexingService,
)

from app.core.dependencies.common import get_unit_of_work

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

def get_document_repository(
    session: AsyncSession = Depends(get_db_session),
) -> DocumentRepository:
    """
    Provides the configured DocumentRepository implementation.
    """

    return PostgresDocumentRepository(
        session=session,
    )


def get_file_storage() -> FileStorage:
    """
    Provides the configured file storage implementation.
    """

    return LocalFileStorage(
        base_directory=settings.knowledge_storage_directory,
    )

def get_document_parser_resolver() -> DocumentParserResolver:
    """
    Provides the configured document parser resolver.
    """

    parsers = {
        DocumentType.TXT: TextDocumentParser(),
        DocumentType.MARKDOWN: MarkdownDocumentParser(),
        DocumentType.PDF: PdfDocumentParser(),
        DocumentType.DOCX: DocxDocumentParser(),
    }

    return DefaultDocumentParserResolver(
        parsers=parsers,
    )

def get_document_chunker() -> DocumentChunker:
    """
    Provides the configured document chunker.
    """

    return LangChainDocumentChunker(
        chunk_size=settings.knowledge_chunk_size,
        chunk_overlap=settings.knowledge_chunk_overlap,
    )

def get_embedding_provider(
) -> EmbeddingProvider:
    """
    Provides the configured embedding provider.
    """

    embedding_model = OpenAIEmbeddings(
        api_key=settings.openai_api_key,
        model=settings.openai_embedding_model,
    )

    return OpenAIEmbeddingProvider(
        embedding_model,
    )

def get_vector_store() -> VectorStore:
    """
    Provides the configured vector store.
    """

    embedding_function = OpenAIEmbeddings(
        api_key=settings.openai_api_key,
        model=settings.openai_embedding_model,
    )

    collection = Chroma(
        collection_name=settings.knowledge_collection_name,
        embedding_function=embedding_function,
        persist_directory=settings.knowledge_chroma_directory,
    )

    return ChromaVectorStore(
        collection=collection,
    )


def get_keyword_store() -> KeywordStore:
    """Provides the persisted BM25 lexical retrieval store."""
    return BM25KeywordStore(directory=settings.knowledge_bm25_directory)

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
    keyword_store: KeywordStore = Depends(
        get_keyword_store,
    ),
    document_repository: DocumentRepository = Depends(
        get_document_repository,
    ),
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
) -> DocumentIndexingService:

    return DocumentIndexingService(
        ingestion_service=ingestion_service,
        chunker=chunker,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        keyword_store=keyword_store,
        document_repository=document_repository,
        unit_of_work=unit_of_work,
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
