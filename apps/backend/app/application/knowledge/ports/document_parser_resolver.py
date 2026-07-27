from abc import ABC, abstractmethod

from app.application.knowledge.enums.document_type import (
    DocumentType,
)
from app.application.knowledge.ports.document_parser import (
    DocumentParser,
)


class DocumentParserResolver(ABC):
    """
    Resolves the parser appropriate for a document type.
    """

    @abstractmethod
    def resolve(
        self,
        document_type: DocumentType,
    ) -> DocumentParser:
        raise NotImplementedError