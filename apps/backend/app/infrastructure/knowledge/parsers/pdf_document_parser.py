from collections.abc import AsyncIterator
from io import BytesIO

from pypdf import PdfReader

from app.application.knowledge.contracts.parsed_document import (
    ParsedDocument,
)
from app.application.knowledge.contracts.parsed_document_section import (
    ParsedDocumentSection,
)
from app.application.knowledge.ports.document_parser import (
    DocumentParser,
)


class PdfDocumentParser(DocumentParser):
    """
    Extracts text from PDF documents.

    Each PDF page is preserved as an individual parsed section
    so page-level metadata remains available for future citations.
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

        reader = PdfReader(
            BytesIO(raw_content)
        )

        sections: list[ParsedDocumentSection] = []

        for page_index, page in enumerate(
            reader.pages,
            start=1,
        ):
            text = page.extract_text() or ""

            normalized_text = text.strip()

            if not normalized_text:
                continue

            sections.append(
                ParsedDocumentSection(
                    content=normalized_text,
                    metadata={
                        "source_filename": filename,
                        "page_number": page_index,
                    },
                )
            )

        return ParsedDocument(
            sections=sections,
            metadata={
                "source_filename": filename,
                "parser": "pdf",
                "page_count": len(reader.pages),
            },
        )