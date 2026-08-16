import asyncio
import json
from pathlib import Path
from uuid import UUID

from app.application.ai.retrieval.document_retrieval_service import (
    DocumentRetrievalService,
)
from app.core.dependencies.knowledge import (
    get_embedding_provider,
    get_vector_store,
)
from app.evaluation.contracts.retrieval_evaluation_case import (
    RetrievalEvaluationCase,
)
from app.evaluation.runner.retrieval_evaluation_runner import (
    RetrievalEvaluationRunner,
)


DATASET_PATH = (
    Path(__file__).parent
    / "datasets"
    / "chroma_chunks.json"
)

EVALUATION_OWNER_ID = UUID(
    "11111111-1111-1111-1111-111111111111"
)

K = 5


async def main() -> None:
    # --------------------------------------------------
    # Load evaluation dataset
    # --------------------------------------------------

    with DATASET_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    cases = [
        RetrievalEvaluationCase(
            id=item["id"],
            question=item["question"],
            relevant_chunk_ids=set(
                item["relevant_chunk_ids"]
            ),
        )
        for item in data
    ]

    # --------------------------------------------------
    # Build production retrieval dependencies
    # --------------------------------------------------

    embedding_provider = get_embedding_provider()
    vector_store = get_vector_store()

    retrieval_service = DocumentRetrievalService(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    # --------------------------------------------------
    # Execute evaluation
    # --------------------------------------------------

    runner = RetrievalEvaluationRunner(
        retrieval_service=retrieval_service,
    )

    report = await runner.run(
        cases=cases,
        owner_id=EVALUATION_OWNER_ID,
        k=K,
    )

    # --------------------------------------------------
    # Print aggregate results
    # --------------------------------------------------

    print()
    print("=" * 70)
    print("RETRIEVAL EVALUATION")
    print("=" * 70)

    print(f"Cases        : {report.total_cases}")
    print(f"K            : {report.k}")
    print(
        f"Precision@{report.k} : "
        f"{report.precision_at_k:.3f}"
    )
    print(
        f"Recall@{report.k}    : "
        f"{report.recall_at_k:.3f}"
    )
    print(
        f"MRR          : "
        f"{report.mean_reciprocal_rank:.3f}"
    )

    # --------------------------------------------------
    # Print individual case results
    # --------------------------------------------------

    print()
    print("-" * 70)
    print("CASE RESULTS")
    print("-" * 70)

    for result in report.results:

        print()
        print(f"Case       : {result.case_id}")
        print(f"Question   : {result.question}")
        print(
            f"Precision@{report.k} : "
            f"{result.precision_at_k:.3f}"
        )
        print(
            f"Recall@{report.k}    : "
            f"{result.recall_at_k:.3f}"
        )
        print(
            f"Reciprocal Rank : "
            f"{result.reciprocal_rank:.3f}"
        )

        print(
            "Retrieved chunks:"
        )

        for chunk in result.retrieved_chunks:

            marker = (
                "✓"
                if chunk.chunk_id
                in result.relevant_chunk_ids
                else " "
            )

            print()
            print(
                f"  [{marker}] Rank {chunk.rank}"
            )
            print(
                f"  Chunk ID        : {chunk.chunk_id}"
            )
            print(
                f"  distance      : "
                f"{chunk.distance:.4f}"
            )
            print(
                f"  Filename        : "
                f"{chunk.filename}"
            )
            print(
                f"  Page            : "
                f"{chunk.page_number}"
            )
            print("  Content:")
            print(
                f"  {chunk.content}"
            )


if __name__ == "__main__":
    asyncio.run(main())