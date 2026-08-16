import json
from pathlib import Path


CORPUS_PATH = (
    Path(__file__).resolve().parent
    / "chroma_chunks.json"
)

EVALUATION_PATH = (
    Path(__file__).resolve().parent
    / "retrieval_eval.json"
)


def main() -> None:

    # --------------------------------------------------
    # Load corpus
    # --------------------------------------------------

    corpus = json.loads(
        CORPUS_PATH.read_text(
            encoding="utf-8",
        )
    )

    corpus_chunk_ids = {
        record["chunk_id"]
        for record in corpus
    }

    # --------------------------------------------------
    # Load evaluation dataset
    # --------------------------------------------------

    evaluation_cases = json.loads(
        EVALUATION_PATH.read_text(
            encoding="utf-8",
        )
    )

    print("=" * 90)
    print("EVALUATION DATASET VALIDATION")
    print("=" * 90)

    print()
    print(f"Corpus chunks : {len(corpus_chunk_ids)}")
    print(f"Evaluation cases: {len(evaluation_cases)}")

    valid_cases = 0
    invalid_cases = 0

    # --------------------------------------------------
    # Validate every case
    # --------------------------------------------------

    for case in evaluation_cases:

        case_id = case["id"]
        question = case["question"]

        expected_ids = set(
            case["relevant_chunk_ids"]
        )

        missing_ids = (
            expected_ids
            - corpus_chunk_ids
        )

        existing_ids = (
            expected_ids
            & corpus_chunk_ids
        )

        print()
        print("-" * 90)
        print(f"Case     : {case_id}")
        print(f"Question : {question}")

        print(
            f"Expected chunks : {len(expected_ids)}"
        )

        print(
            f"Existing chunks : {len(existing_ids)}"
        )

        print(
            f"Missing chunks  : {len(missing_ids)}"
        )

        if missing_ids:

            invalid_cases += 1

            print()
            print("MISSING CHUNK IDS:")

            for chunk_id in sorted(missing_ids):
                print(
                    f"  [MISSING] {chunk_id}"
                )

        else:

            valid_cases += 1

            print()
            print("STATUS: VALID")

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------

    print()
    print("=" * 90)
    print("SUMMARY")
    print("=" * 90)

    print(
        f"Valid cases  : {valid_cases}"
    )

    print(
        f"Invalid cases: {invalid_cases}"
    )

    print()

    if invalid_cases == 0:
        print(
            "RESULT: Evaluation dataset is synchronized "
            "with the current corpus."
        )
    else:
        print(
            "RESULT: Evaluation dataset contains stale "
            "or invalid chunk IDs."
        )


if __name__ == "__main__":
    main()