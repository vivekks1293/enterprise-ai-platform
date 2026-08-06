from langchain_openai import OpenAIEmbeddings

from app.application.knowledge.contracts.embedding_vector import (
    EmbeddingVector,
)
from app.application.knowledge.contracts.vector_record import (
    VectorRecord,
)
from app.application.knowledge.contracts.document_chunk import (
    DocumentChunk,
)
from app.application.knowledge.ports.embedding_provider import (
    EmbeddingProvider,
)


class OpenAIEmbeddingProvider(
    EmbeddingProvider,
):
    """
    Generates embeddings using OpenAI.
    """

    def __init__(
        self,
        embedding_model: OpenAIEmbeddings,
    ) -> None:

        self._embedding_model = embedding_model

    async def embed(
        self,
        chunks: list[DocumentChunk],
    ) -> list[VectorRecord]:

        texts = [
            chunk.content
            for chunk in chunks
        ]

        vectors = await self._embedding_model.aembed_documents(
            texts
        )

        records: list[VectorRecord] = []

        for chunk, vector in zip(
            chunks,
            vectors,
            strict=True,
        ):

            records.append(
                VectorRecord(
                    chunk=chunk,
                    embedding=EmbeddingVector(
                        values=vector,
                    ),
                )
            )

        return records