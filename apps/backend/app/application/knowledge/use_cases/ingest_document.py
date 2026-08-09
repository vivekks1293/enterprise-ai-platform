from app.application.common.ports.unit_of_work import UnitOfWork
from app.application.knowledge.dto.ingest_document import (
    IngestDocumentRequest,
    IngestDocumentResponse,
)
from app.application.knowledge.exceptions import (
    DocumentNotFoundError, DocumentParsingError
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
from app.domain.knowledge.repositories.document_repository import (
    DocumentRepository,
)


class IngestDocumentUseCase:
    """
    Extracts normalized content from a stored knowledge document.
    """

    def __init__(
        self,
        document_repository: DocumentRepository,
        file_storage: FileStorage,
        document_type_resolver: DocumentTypeResolver,
        document_parser_resolver: DocumentParserResolver,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._document_repository = document_repository
        self._file_storage = file_storage
        self._document_type_resolver = document_type_resolver
        self._document_parser_resolver = document_parser_resolver
        self._unit_of_work = unit_of_work

    async def execute(
        self,
        request: IngestDocumentRequest,
    ) -> IngestDocumentResponse:

        # --------------------------------------------------
        # 1. Retrieve document + validate ownership
        # --------------------------------------------------

        document = await self._document_repository.get_by_id(
            document_id=request.document_id,
            owner_id=request.owner_id,
        )

        if document is None:
            raise DocumentNotFoundError()

        # --------------------------------------------------
        # 2. Verify physical content exists
        # --------------------------------------------------

        exists = await self._file_storage.exists(
            storage_key=document.storage_key,
        )

        if not exists:
            raise DocumentNotFoundError()

        # --------------------------------------------------
        # 3. Resolve document type
        # --------------------------------------------------

        document_type = self._document_type_resolver.resolve(
            document.original_filename,
        )

        # --------------------------------------------------
        # 4. Resolve parser
        # --------------------------------------------------

        parser = self._document_parser_resolver.resolve(
            document_type,
        )

        # --------------------------------------------------
        # 5. Mark processing
        # --------------------------------------------------

        document.mark_indexing()

        await self._document_repository.update(document)
        await self._unit_of_work.commit()

        try:

            # ----------------------------------------------
            # 6. Read stored content
            # ----------------------------------------------

            content = self._file_storage.read(
                storage_key=document.storage_key,
            )

            # ----------------------------------------------
            # 7. Parse document
            # ----------------------------------------------

            parsed_document = await parser.parse(
                content=content,
                filename=document.original_filename,
            )

            if not parsed_document.sections:
                raise DocumentParsingError()

            # ----------------------------------------------
            # 8. Mark successfully processed
            # ----------------------------------------------

            document.mark_processed()

            await self._document_repository.update(document)
            await self._unit_of_work.commit()

        except Exception:

            document.mark_failed()

            await self._document_repository.update(document)
            await self._unit_of_work.commit()

            raise

        return IngestDocumentResponse(
            document_id=document.id,
            status=document.status.value,
            parsed_document=parsed_document,
        )