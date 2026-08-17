import asyncio
import argparse
import json
from pathlib import Path
from uuid import UUID

from app.application.ai.retrieval.document_retrieval_service import (
    DocumentRetrievalService,
)
from app.core.dependencies.knowledge import (
    get_embedding_provider,
    get_keyword_store,
    get_vector_store,
)
from app.evaluation.contracts.retrieval_evaluation_case import (
    RetrievalEvaluationCase,
)
from app.evaluation.runner.retrieval_evaluation_runner import (
    RetrievalEvaluationRunner,
)


# ============================================================
# Paths
# ============================================================

DATASET_PATH = (
    Path(__file__).parent
    / "datasets"
    / "retrieval_eval.json"
)

REPORT_DIRECTORY = (
    Path(__file__).parent
    / "reports"
)

# ============================================================
# Evaluation configuration
# ============================================================

EVALUATION_OWNER_ID = UUID(
    "11111111-1111-1111-1111-111111111111"
)

K = 20


# ============================================================
# Dataset loading
# ============================================================

def load_evaluation_cases() -> list[RetrievalEvaluationCase]:
    """
    Loads retrieval evaluation cases from the
    evaluation dataset.
    """

    with DATASET_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            "Evaluation dataset must be a JSON list."
        )

    cases: list[RetrievalEvaluationCase] = []

    for index, item in enumerate(
        data,
        start=1,
    ):
        if not isinstance(item, dict):
            raise ValueError(
                f"Evaluation case #{index} must be a JSON object."
            )

        required_fields = {
            "id",
            "question",
            "relevant_chunk_ids",
        }

        missing_fields = (
            required_fields - item.keys()
        )

        if missing_fields:
            raise ValueError(
                f"Evaluation case #{index} is missing "
                f"required fields: "
                f"{sorted(missing_fields)}"
            )

        if not isinstance(
            item["relevant_chunk_ids"],
            list,
        ):
            raise ValueError(
                f"Evaluation case '{item['id']}' must have "
                "'relevant_chunk_ids' as a list."
            )

        cases.append(
            RetrievalEvaluationCase(
                id=item["id"],
                question=item["question"],
                relevant_chunk_ids=set(
                    item["relevant_chunk_ids"]
                ),
            )
        )

    return cases


# ============================================================
# Report serialization
# ============================================================

def build_report_json(report) -> dict:
    """
    Converts the evaluation report domain object
    into a JSON-serializable structure.
    """

    cases: list[dict] = []

    for result in report.results:

        retrieved_chunks: list[dict] = []

        for chunk in result.retrieved_chunks:

            retrieved_chunks.append(
                {
                    "rank": chunk.rank,
                    "chunk_id": chunk.chunk_id,
                    "score": chunk.score,
                    "filename": chunk.filename,
                    "page_number": chunk.page_number,
                    "content": chunk.content,
                    "is_relevant": (
                        chunk.chunk_id
                        in result.relevant_chunk_ids
                    ),
                }
            )

        cases.append(
            {
                "case_id": result.case_id,
                "question": result.question,
                "precision_at_k": result.precision_at_k,
                "recall_at_k": result.recall_at_k,
                "reciprocal_rank": result.reciprocal_rank,
                "relevant_chunk_ids": sorted(
                    result.relevant_chunk_ids
                ),
                "retrieved_chunks": retrieved_chunks,
            }
        )

    return {
        "retrieval_method": report.retrieval_method,
        "summary": {
            "total_cases": report.total_cases,
            "k": report.k,
            "precision_at_k": report.precision_at_k,
            "recall_at_k": report.recall_at_k,
            "mean_reciprocal_rank": (
                report.mean_reciprocal_rank
            ),
        },
        "cases": cases,
    }


def save_report(report) -> None:
    """
    Saves the evaluation report as formatted JSON.
    """

    REPORT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_data = build_report_json(report)

    report_path = REPORT_DIRECTORY / f"{report.retrieval_method}_top{report.k}.json"
    report_path.write_text(
        json.dumps(
            report_data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print(
        f"Evaluation report saved to:"
    )
    print(
        report_path
    )


# ============================================================
# Main evaluation
# ============================================================

async def main(retrieval_method: str = "semantic") -> None:

    # --------------------------------------------------------
    # Load evaluation dataset
    # --------------------------------------------------------

    cases = load_evaluation_cases()

    print(
        f"Loaded {len(cases)} evaluation cases."
    )

    # --------------------------------------------------------
    # Build production retrieval dependencies
    # --------------------------------------------------------

    embedding_provider = get_embedding_provider()

    vector_store = get_vector_store()
    keyword_store = get_keyword_store()

    retrieval_service = DocumentRetrievalService(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        keyword_store=keyword_store,
    )

    # --------------------------------------------------------
    # Create evaluation runner
    # --------------------------------------------------------

    runner = RetrievalEvaluationRunner(
        retrieval_service=retrieval_service,
    )

    # --------------------------------------------------------
    # Execute evaluation
    # --------------------------------------------------------

    report = await runner.run(
        cases=cases,
        owner_id=EVALUATION_OWNER_ID,
        k=K,
        retrieval_method=retrieval_method,
    )

    # --------------------------------------------------------
    # Save JSON report
    # --------------------------------------------------------

    save_report(report)

    # --------------------------------------------------------
    # Print aggregate results
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("RETRIEVAL EVALUATION")
    print("=" * 70)

    print(
        f"Cases        : {report.total_cases}"
    )

    print(
        f"K            : {report.k}"
    )

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

    # --------------------------------------------------------
    # Print individual case results
    # --------------------------------------------------------

    print()
    print("-" * 70)
    print("CASE RESULTS")
    print("-" * 70)

    for result in report.results:

        print()
        print(
            f"Case       : {result.case_id}"
        )

        print(
            f"Question   : {result.question}"
        )

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
                f"  Chunk ID        : "
                f"{chunk.chunk_id}"
            )

            print(
                f"  score           : "
                f"{chunk.score:.4f}"
            )

            print(
                f"  Filename        : "
                f"{chunk.filename}"
            )

            print(
                f"  Page            : "
                f"{chunk.page_number}"
            )

            print(
                "  Content:"
            )

            print(
                f"  {chunk.content}"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--method",
        choices=("semantic", "keyword", "hybrid"),
        default="semantic",
    )
    arguments = parser.parse_args()
    asyncio.run(main(arguments.method))
