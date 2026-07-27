from collections.abc import AsyncIterator

from app.application.knowledge.contracts.parsed_document import (
    ParsedDocument,
)
from app.application.knowledge.contracts.parsed_document_section import (
    ParsedDocumentSection,
)
from app.application.knowledge.ports.document_parser import (
    DocumentParser,
)


class TextDocumentParser(DocumentParser):
    """
    Parses plain-text documents into normalized document content.
    """

    async def parse(
        self,
        *,
        content: AsyncIterator[bytes],
        filename: str,
    ) -> ParsedDocument:

        raw_content = bytearray()

        async for chunk in content:
            raw_content.extend(chunk)

        text = raw_content.decode("utf-8")

        normalized_text = text.strip()

        section = ParsedDocumentSection(
            content=normalized_text,
            metadata={
                "source_filename": filename,
            },
        )

        return ParsedDocument(
            sections=[section],
            metadata={
                "source_filename": filename,
                "parser": "text",
            },
        )