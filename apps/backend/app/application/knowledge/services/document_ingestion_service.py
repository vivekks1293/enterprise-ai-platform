from app.application.knowledge.contracts.parsed_document import (
    ParsedDocument,
)
from app.application.knowledge.exceptions import (
    DocumentNotFoundError,
)
from app.application.knowledge.ports.document_parser_resolver import (
    DocumentParserResolver,
)
from app.application.knowledge.ports.file_storage import (
    FileStorage,
)
from app.application.knowledge.services.document_type_resolver import (
    DocumentTypeResolver,
)
from app.domain.knowledge.entities.document import Document


class DocumentIngestionService:
    """
    Reads a stored document and converts it into a ParsedDocument.

    This service encapsulates all parsing logic so that multiple
    use cases can reuse the same ingestion pipeline.
    """

    def __init__(
        self,
        *,
        file_storage: FileStorage,
        document_type_resolver: DocumentTypeResolver,
        parser_resolver: DocumentParserResolver,
    ) -> None:
        self._file_storage = file_storage
        self._document_type_resolver = document_type_resolver
        self._parser_resolver = parser_resolver

    async def ingest(
        self,
        document: Document,
    ) -> ParsedDocument:
        """
        Reads and parses a stored document.
        """

        exists = await self._file_storage.exists(
            storage_key=document.storage_key,
        )

        if not exists:
            raise DocumentNotFoundError()

        # content = await self._file_storage.read(
        #     storage_key=document.storage_key,
        # )
        content = bytearray()

        async for chunk in self._file_storage.read(
            storage_key=document.storage_key,
        ):
            content.extend(chunk)

        document_type = self._document_type_resolver.resolve(
            document.original_filename,
        )

        parser = self._parser_resolver.resolve(
            document_type,
        )

        parsed_document = await parser.parse(
            content=bytes(content),
            filename=document.original_filename,
        )

        return parsed_document