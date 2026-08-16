"""One-time backfill of the BM25 corpus from the existing Chroma collection."""

import asyncio
import json
from collections import Counter
from pathlib import Path

import chromadb

from app.application.knowledge.contracts.document_chunk import DocumentChunk
from app.core.config.settings import settings
from app.core.dependencies.knowledge import get_keyword_store
from app.infrastructure.knowledge.vectorstore.chroma_metadata_mapper import (
    ChromaMetadataMapper,
)


KNOWN_CHUNK_ID = "76313112-0230-56de-995f-320053466b7a"


def load_chroma_chunks() -> list[DocumentChunk]:
    """Reads every existing Chroma record without modifying the collection."""
    client = chromadb.PersistentClient(path=settings.knowledge_chroma_directory)
    collection = client.get_collection(name=settings.knowledge_collection_name)
    result = collection.get(include=["documents", "metadatas"])

    documents = result.get("documents", [])
    metadatas = result.get("metadatas", [])
    if len(documents) != len(metadatas):
        raise RuntimeError("Chroma returned mismatched documents and metadata.")

    return [
        DocumentChunk(
            content=document or "",
            metadata=ChromaMetadataMapper.from_chroma(metadata),
        )
        for document, metadata in zip(documents, metadatas, strict=True)
    ]


def print_chroma_summary(chunks: list[DocumentChunk]) -> None:
    owner_counts = Counter(str(chunk.metadata.owner_id) for chunk in chunks)
    document_ids = {chunk.metadata.document_id for chunk in chunks}

    print(f"Total Chroma chunks: {len(chunks)}")
    print(f"Unique documents: {len(document_ids)}")
    print("Owner IDs:")
    for owner_id, count in sorted(owner_counts.items()):
        print(f"  {owner_id}: {count}")


def bm25_corpus_path() -> Path:
    return Path(settings.knowledge_bm25_directory) / "bm25_corpus.json"


def persisted_bm25_records() -> list[dict]:
    corpus_path = bm25_corpus_path()
    if not corpus_path.exists():
        return []
    return json.loads(corpus_path.read_text(encoding="utf-8"))


async def main() -> None:
    chunks = load_chroma_chunks()
    if not chunks:
        raise RuntimeError("The configured Chroma collection contains no chunks.")

    print_chroma_summary(chunks)

    existing_record_count = len(persisted_bm25_records())
    print(f"Existing BM25 chunks: {existing_record_count}")

    keyword_store = get_keyword_store()
    await keyword_store.add(chunks)

    corpus_path = bm25_corpus_path()
    records = persisted_bm25_records()
    expected_chunk_ids = {chunk.metadata.chunk_id for chunk in chunks}
    actual_chunk_ids = {record["chunk_id"] for record in records}

    if len(records) != len(chunks):
        raise RuntimeError(
            "BM25 corpus size does not match the Chroma chunk count. "
            f"Chroma={len(chunks)}, BM25={len(records)}."
        )
    if actual_chunk_ids != expected_chunk_ids:
        raise RuntimeError("BM25 corpus chunk IDs do not match Chroma chunk IDs.")
    if KNOWN_CHUNK_ID not in actual_chunk_ids:
        raise RuntimeError(f"Known chunk ID is missing: {KNOWN_CHUNK_ID}")

    print(f"Chroma chunks read : {len(chunks)}")
    print(f"BM25 chunks written: {len(records)}")
    print(f"BM25 persistence path: {corpus_path.resolve()}")
    print(f"BM25 corpus size: {len(records)}")
    print(f"Known chunk present: {KNOWN_CHUNK_ID}")


if __name__ == "__main__":
    asyncio.run(main())
