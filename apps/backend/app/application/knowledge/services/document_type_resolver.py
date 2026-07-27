from pathlib import Path

from app.application.knowledge.enums.document_type import (
    DocumentType,
)


class DocumentTypeResolver:
    """
    Resolves supported document types from filenames.
    """

    _EXTENSION_MAP = {
        ".pdf": DocumentType.PDF,
        ".docx": DocumentType.DOCX,
        ".txt": DocumentType.TXT,
        ".md": DocumentType.MARKDOWN,
        ".markdown": DocumentType.MARKDOWN,
    }

    def resolve(
        self,
        filename: str,
    ) -> DocumentType:

        extension = Path(filename).suffix.lower()

        document_type = self._EXTENSION_MAP.get(extension)

        if document_type is None:
            raise ValueError(
                f"Unsupported document type: {extension}"
            )

        return document_type