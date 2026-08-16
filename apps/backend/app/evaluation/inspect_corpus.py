import json
from collections import Counter
from pathlib import Path


INPUT_PATH = (
    Path(__file__).resolve().parent
    / "chroma_chunks.json"
)


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Corpus file not found: {INPUT_PATH}"
        )

    records = json.loads(
        INPUT_PATH.read_text(
            encoding="utf-8",
        )
    )

    if not records:
        print("No chunks found.")
        return

    # --------------------------------------------------
    # Basic statistics
    # --------------------------------------------------

    documents = Counter(
        record["filename"]
        for record in records
    )

    document_ids = Counter(
        record["document_id"]
        for record in records
    )

    chunk_lengths = [
        len(record.get("content") or "")
        for record in records
    ]

    empty_chunks = [
        record
        for record in records
        if not (record.get("content") or "").strip()
    ]

    missing_metadata = {
        field: sum(
            1
            for record in records
            if record.get(field) is None
        )
        for field in [
            "chroma_id",
            "document_id",
            "chunk_id",
            "filename",
            "chunk_index",
            "owner_id",
        ]
    }

    # --------------------------------------------------
    # Duplicate detection
    # --------------------------------------------------

    content_counts = Counter(
        (record.get("content") or "").strip()
        for record in records
        if (record.get("content") or "").strip()
    )

    duplicate_groups = {
        content: count
        for content, count in content_counts.items()
        if count > 1
    }

    # --------------------------------------------------
    # Print report
    # --------------------------------------------------

    print("=" * 80)
    print("CORPUS INSPECTION")
    print("=" * 80)

    print()
    print(f"Total chunks   : {len(records)}")
    print(f"Total documents: {len(documents)}")

    print()
    print("-" * 80)
    print("DOCUMENT DISTRIBUTION")
    print("-" * 80)

    for filename, count in documents.most_common():
        print(
            f"{count:5d} chunks | {filename}"
        )

    print()
    print("-" * 80)
    print("CHUNK SIZE")
    print("-" * 80)

    print(
        f"Minimum length : {min(chunk_lengths)}"
    )
    print(
        f"Maximum length : {max(chunk_lengths)}"
    )
    print(
        f"Average length : "
        f"{sum(chunk_lengths) / len(chunk_lengths):.1f}"
    )

    print()
    print("-" * 80)
    print("EMPTY CHUNKS")
    print("-" * 80)

    print(
        f"Empty chunks: {len(empty_chunks)}"
    )

    print()
    print("-" * 80)
    print("MISSING METADATA")
    print("-" * 80)

    for field, count in missing_metadata.items():
        print(
            f"{field:15s}: {count}"
        )

    print()
    print("-" * 80)
    print("DUPLICATE CONTENT")
    print("-" * 80)

    print(
        f"Duplicate content groups: "
        f"{len(duplicate_groups)}"
    )

    if duplicate_groups:
        for content, count in list(
            duplicate_groups.items()
        )[:10]:
            print()
            print(f"Occurrences: {count}")
            print(
                content[:300].replace(
                    "\n",
                    " ",
                )
            )

    # --------------------------------------------------
    # Chunk-index continuity
    # --------------------------------------------------

    print()
    print("-" * 80)
    print("CHUNK INDEX CHECK")
    print("-" * 80)

    records_by_document: dict[str, list[dict]] = {}

    for record in records:
        records_by_document.setdefault(
            record["document_id"],
            [],
        ).append(record)

    for document_id, chunks in records_by_document.items():

        indexes = sorted(
            record["chunk_index"]
            for record in chunks
            if record.get("chunk_index") is not None
        )

        if not indexes:
            continue

        expected = list(
            range(
                min(indexes),
                max(indexes) + 1,
            )
        )

        missing = sorted(
            set(expected) - set(indexes)
        )

        filename = chunks[0]["filename"]

        print(
            f"{filename}: "
            f"{len(indexes)} chunks"
        )

        if missing:
            print(
                f"  Missing indexes: "
                f"{missing[:20]}"
            )
        else:
            print(
                "  Index sequence: OK"
            )


if __name__ == "__main__":
    main()