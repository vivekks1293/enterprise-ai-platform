import json
import re
from pathlib import Path
from uuid import UUID

from rank_bm25 import BM25Okapi

from app.application.knowledge.contracts.chunk_metadata import ChunkMetadata
from app.application.knowledge.contracts.document_chunk import DocumentChunk
from app.application.knowledge.contracts.retrieved_chunk import RetrievedChunk
from app.application.knowledge.contracts.vector_search_filter import VectorSearchFilter
from app.application.knowledge.contracts.vector_search_result import VectorSearchResult
from app.application.knowledge.ports.keyword_store import KeywordStore


class BM25KeywordStore(KeywordStore):
    """Persistent, development-focused BM25 index over indexed document chunks."""

    _TOKEN_PATTERN = re.compile(r"\b\w+\b", re.UNICODE)
    _CORPUS_FILENAME = "bm25_corpus.json"

    def __init__(self, directory: str | Path) -> None:
        self._directory = Path(directory)
        self._directory.mkdir(parents=True, exist_ok=True)
        self._corpus_path = self._directory / self._CORPUS_FILENAME
        self._chunks_by_key = self._load_corpus()
        self._rebuild_indexes()

    async def add(self, chunks: list[DocumentChunk]) -> None:
        if not chunks:
            return

        for chunk in chunks:
            self._chunks_by_key[self._key(chunk.metadata)] = chunk

        self._persist_corpus()
        self._rebuild_indexes()

    async def search(
        self,
        *,
        query: str,
        filter: VectorSearchFilter,
        top_k: int,
    ) -> VectorSearchResult:
        if top_k <= 0 or not (query_tokens := self._tokenize(query)):
            return VectorSearchResult(chunks=[])

        owner_index = self._owner_indexes.get(filter.owner_id)
        if owner_index is None:
            return VectorSearchResult(chunks=[])

        candidates, index = owner_index
        if filter.document_id is not None:
            candidates = [
                chunk
                for chunk in candidates
                if chunk.metadata.document_id == filter.document_id
            ]
            index = BM25Okapi(
                [self._tokenize(chunk.content) for chunk in candidates]
            ) if candidates else None
        if not candidates:
            return VectorSearchResult(chunks=[])

        assert index is not None
        scored = sorted(
            zip(index.get_scores(query_tokens), candidates, strict=True),
            key=lambda item: float(item[0]),
            reverse=True,
        )

        return VectorSearchResult(
            chunks=[
                RetrievedChunk(
                    content=chunk.content,
                    metadata=chunk.metadata,
                    score=float(score),
                )
                for score, chunk in scored[:top_k]
            ]
        )

    @classmethod
    def _tokenize(cls, value: str) -> list[str]:
        return cls._TOKEN_PATTERN.findall(value.lower())

    @staticmethod
    def _key(metadata: ChunkMetadata) -> str:
        return f"{metadata.document_id}:{metadata.chunk_id}"

    def _rebuild_indexes(self) -> None:
        # BM25 is rebuilt from the persisted corpus on startup and after every upsert.
        chunks_by_owner: dict[UUID, list[DocumentChunk]] = {}
        for chunk in self._chunks_by_key.values():
            chunks_by_owner.setdefault(chunk.metadata.owner_id, []).append(chunk)
        self._owner_indexes: dict[UUID, tuple[list[DocumentChunk], BM25Okapi]] = {
            owner_id: (
                chunks,
                BM25Okapi([self._tokenize(chunk.content) for chunk in chunks]),
            )
            for owner_id, chunks in chunks_by_owner.items()
        }

    def _load_corpus(self) -> dict[str, DocumentChunk]:
        if not self._corpus_path.exists():
            return {}

        with self._corpus_path.open(encoding="utf-8") as corpus_file:
            records = json.load(corpus_file)

        chunks: dict[str, DocumentChunk] = {}
        for record in records:
            metadata = ChunkMetadata(
                document_id=UUID(record["document_id"]),
                owner_id=UUID(record["owner_id"]),
                filename=record["filename"],
                chunk_id=record["chunk_id"],
                chunk_index=record["chunk_index"],
                page_number=record["page_number"],
            )
            chunk = DocumentChunk(content=record["content"], metadata=metadata)
            chunks[self._key(metadata)] = chunk
        return chunks

    def _persist_corpus(self) -> None:
        records = [
            {
                "chunk_id": chunk.metadata.chunk_id,
                "document_id": str(chunk.metadata.document_id),
                "owner_id": str(chunk.metadata.owner_id),
                "filename": chunk.metadata.filename,
                "chunk_index": chunk.metadata.chunk_index,
                "page_number": chunk.metadata.page_number,
                "content": chunk.content,
            }
            for chunk in self._chunks_by_key.values()
        ]
        temporary_path = self._corpus_path.with_suffix(".tmp")
        temporary_path.write_text(
            json.dumps(records, ensure_ascii=False), encoding="utf-8"
        )
        temporary_path.replace(self._corpus_path)
