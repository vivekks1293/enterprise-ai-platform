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