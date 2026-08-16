import json
from pathlib import Path

import chromadb

from app.core.config.settings import settings


DATASET_PATH = (
    Path(__file__).parent
    / "datasets"
    / "chroma_chunks.json"
)


def main() -> None:

    # --------------------------------------------------
    # Load evaluation dataset
    # --------------------------------------------------

    with DATASET_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        cases = json.load(file)

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
    # Load all indexed chunks
    # --------------------------------------------------

    stored = collection.get(
        include=[
            "documents",
            "metadatas",
        ],
    )

    stored_documents = stored.get(
        "documents",
        [],
    )

    stored_metadatas = stored.get(
        "metadatas",
        [],
    )

    # --------------------------------------------------
    # Build lookup by application-level chunk_id
    # --------------------------------------------------

    chunks_by_id = {}

    for document, metadata in zip(
        stored_documents,
        stored_metadatas,
        strict=True,
    ):
        chunk_id = metadata.get("chunk_id")

        if chunk_id is None:
            continue

        chunks_by_id[chunk_id] = {
            "document": document,
            "metadata": metadata,
        }

    # --------------------------------------------------
    # Inspect every evaluation case
    # --------------------------------------------------

    print()
    print("=" * 100)
    print("EVALUATION DATASET INSPECTION")
    print("=" * 100)

    for case in cases:

        print()
        print("=" * 100)
        print(f"CASE: {case['id']}")
        print("=" * 100)

        print()
        print("QUESTION:")
        print(case["question"])

        print()
        print("EXPECTED RELEVANT CHUNKS:")
        print("-" * 100)

        relevant_ids = case["relevant_chunk_ids"]

        for chunk_id in relevant_ids:

            chunk = chunks_by_id.get(chunk_id)

            if chunk is None:
                print()
                print(
                    f"WARNING: Chunk ID not found: "
                    f"{chunk_id}"
                )
                continue

            metadata = chunk["metadata"]
            document = chunk["document"]

            print()
            print(f"Chunk ID : {chunk_id}")
            print(
                f"Filename : "
                f"{metadata.get('filename')}"
            )
            print(
                f"Page     : "
                f"{metadata.get('page_number')}"
            )
            print(
                f"Index    : "
                f"{metadata.get('chunk_index')}"
            )

            print()
            print("CONTENT:")
            print(document)

            print()
            print("-" * 100)


if __name__ == "__main__":
    main()