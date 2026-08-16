import json
from pathlib import Path

from app.evaluation.contracts.retrieval_evaluation_case import (
    RetrievalEvaluationCase,
)


class RetrievalDatasetLoader:
    """
    Loads retrieval evaluation cases from a JSON file.
    """

    @staticmethod
    def load(
        path: Path,
    ) -> list[RetrievalEvaluationCase]:
        """
        Loads and validates the retrieval evaluation dataset.
        """

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        return [
            RetrievalEvaluationCase(
                id=item["id"],
                question=item["question"],
                relevant_chunk_ids=set(
                    item["relevant_chunk_ids"]
                ),
            )
            for item in data
        ]