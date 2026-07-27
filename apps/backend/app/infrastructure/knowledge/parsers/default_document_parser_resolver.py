from app.application.knowledge.enums.document_type import (
    DocumentType,
)
from app.application.knowledge.ports.document_parser import (
    DocumentParser,
)
from app.application.knowledge.ports.document_parser_resolver import (
    DocumentParserResolver,
)


class DefaultDocumentParserResolver(DocumentParserResolver):
    """
    Resolves document parsers based on document type.
    """

    def __init__(
        self,
        parsers: dict[DocumentType, DocumentParser],
    ) -> None:
        self._parsers = parsers

    def resolve(
        self,
        document_type: DocumentType,
    ) -> DocumentParser:

        parser = self._parsers.get(document_type)

        if parser is None:
            raise ValueError(
                f"No parser configured for document type: "
                f"{document_type.value}"
            )

        return parser