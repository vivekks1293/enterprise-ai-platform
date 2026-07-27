from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from app.application.knowledge.contracts.parsed_document import (
    ParsedDocument,
)


class DocumentParser(ABC):
    """
    Extracts normalized content from a stored document.

    Implementations may use LangChain document loaders,
    PyPDF, python-docx, or another parsing technology.
    """

    @abstractmethod
    async def parse(
        self,
        *,
        content: AsyncIterator[bytes],
        filename: str,
    ) -> ParsedDocument:
        raise NotImplementedError