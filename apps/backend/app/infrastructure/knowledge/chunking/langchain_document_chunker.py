from uuid import uuid5

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)

from app.application.knowledge.contracts.chunk_metadata import (
    ChunkMetadata,
)
from app.application.knowledge.contracts.document_chunk import (
    DocumentChunk,
)
from app.application.knowledge.contracts.parsed_document import (
    ParsedDocument,
)
from app.application.knowledge.ports.document_chunker import (
    DocumentChunker,
)
from app.domain.knowledge.entities.document import (
    Document,
)


class LangChainDocumentChunker(DocumentChunker):
    """
    Splits parsed documents into overlapping chunks
    using LangChain's RecursiveCharacterTextSplitter.
    """

    def __init__(
        self,
        *,
        chunk_size: int,
        chunk_overlap: int,
    ) -> None:
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    async def chunk(
        self,
        *,
        document: Document,
        parsed_document: ParsedDocument,
    ) -> list[DocumentChunk]:
        """
        Splits a parsed document into chunks and assigns
        deterministic metadata to each chunk.
        """

        chunks: list[DocumentChunk] = []

        chunk_index = 0

        for section in parsed_document.sections:

            texts = self._splitter.split_text(
                section.content,
            )

            page_number = section.metadata.get(
                "page_number",
            )

            for text in texts:

                # --------------------------------------------------
                # Generate deterministic chunk identity
                # --------------------------------------------------

                chunk_id = str(
                    uuid5(
                        document.id,
                        f"chunk:{chunk_index}",
                    )
                )

                metadata = ChunkMetadata(
                    document_id=document.id,
                    owner_id=document.owner_id,
                    filename=document.original_filename,
                    chunk_id=chunk_id,
                    chunk_index=chunk_index,
                    page_number=page_number,
                )

                chunks.append(
                    DocumentChunk(
                        content=text,
                        metadata=metadata,
                    )
                )

                chunk_index += 1

        return chunks