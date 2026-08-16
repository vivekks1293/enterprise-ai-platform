import json
from pathlib import Path

import chromadb

from app.core.config.settings import settings


TXT_OUTPUT_PATH = (
    Path(__file__).resolve().parent
    / "chroma_chunks.txt"
)

JSON_OUTPUT_PATH = (
    Path(__file__).resolve().parent
    / "chroma_chunks.json"
)


def main() -> None:
    """
    Exports the current Chroma knowledge base into:

    1. A human-readable TXT file for inspection.
    2. A structured JSON file for evaluation dataset creation.

    This utility is read-only.
    It does not modify the Chroma collection.
    """

    # --------------------------------------------------
    # Open existing Chroma collection
    # --------------------------------------------------

    client = chromadb.PersistentClient(
        path=settings.knowledge_chroma_directory,
    )

    collection = client.get_collection(
        name=settings.knowledge_collection_name,
    )

    # --------------------------------------------------
    # Read all indexed chunks
    # --------------------------------------------------

    result = collection.get(
        include=[
            "documents",
            "metadatas",
        ],
    )

    ids = result.get("ids", [])
    documents = result.get("documents", [])
    metadatas = result.get("metadatas", [])

    if not ids:
        print(
            "No chunks found in the Chroma collection."
        )
        return

    # --------------------------------------------------
    # Prepare output structures
    # --------------------------------------------------

    lines: list[str] = []

    chunk_records: list[dict] = []

    # --------------------------------------------------
    # Header
    # --------------------------------------------------

    lines.append("=" * 100)
    lines.append("CHROMA KNOWLEDGE BASE EXPORT")
    lines.append("=" * 100)
    lines.append("")
    lines.append(
        f"Collection: "
        f"{settings.knowledge_collection_name}"
    )
    lines.append(
        f"Total chunks: {len(ids)}"
    )
    lines.append("")

    # --------------------------------------------------
    # Process chunks
    # --------------------------------------------------

    for index, (
        chroma_id,
        document,
        metadata,
    ) in enumerate(
        zip(
            ids,
            documents,
            metadatas,
            strict=True,
        ),
        start=1,
    ):

        # --------------------------------------------------
        # Human-readable TXT record
        # --------------------------------------------------

        lines.append("-" * 100)
        lines.append(f"CHUNK #{index}")
        lines.append("-" * 100)

        lines.append(
            f"Chroma ID: {chroma_id}"
        )

        lines.append(
            f"Document ID: "
            f"{metadata.get('document_id')}"
        )

        lines.append(
            f"Chunk ID: "
            f"{metadata.get('chunk_id')}"
        )

        lines.append(
            f"Filename: "
            f"{metadata.get('filename')}"
        )

        lines.append(
            f"Chunk Index: "
            f"{metadata.get('chunk_index')}"
        )

        lines.append(
            f"Page Number: "
            f"{metadata.get('page_number')}"
        )

        lines.append(
            f"Owner ID: "
            f"{metadata.get('owner_id')}"
        )

        lines.append("")
        lines.append("CONTENT:")
        lines.append(document or "")
        lines.append("")

        # --------------------------------------------------
        # Structured JSON record
        # --------------------------------------------------

        chunk_records.append(
            {
                "chroma_id": chroma_id,
                "document_id": metadata.get(
                    "document_id"
                ),
                "chunk_id": metadata.get(
                    "chunk_id"
                ),
                "filename": metadata.get(
                    "filename"
                ),
                "chunk_index": metadata.get(
                    "chunk_index"
                ),
                "page_number": metadata.get(
                    "page_number"
                ),
                "owner_id": metadata.get(
                    "owner_id"
                ),
                "content": document or "",
            }
        )

    # --------------------------------------------------
    # Write human-readable TXT
    # --------------------------------------------------

    TXT_OUTPUT_PATH.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    # --------------------------------------------------
    # Write structured JSON
    # --------------------------------------------------

    JSON_OUTPUT_PATH.write_text(
        json.dumps(
            chunk_records,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # --------------------------------------------------
    # Final output
    # --------------------------------------------------

    print(
        f"Exported {len(ids)} chunks."
    )

    print(
        f"TXT : {TXT_OUTPUT_PATH}"
    )

    print(
        f"JSON: {JSON_OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()