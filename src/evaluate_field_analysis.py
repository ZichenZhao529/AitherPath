# src/evaluate_field_analysis.py

import json
from pathlib import Path

from src.expected_mappings import EXPECTED_MAPPINGS


OUTPUT_DIR = Path("outputs/field_analysis")


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_one_file(file_key: str, expected_mapping: dict) -> dict:
    json_path = OUTPUT_DIR / f"{file_key}.json"

    if not json_path.exists():
        return {
            "file_key": file_key,
            "status": "missing_output",
            "total": 0,
            "correct": 0,
            "errors": [],
        }

    data = load_json(json_path)

    predicted_columns = data.get("columns", [])
    predicted_map = {
        item["column_name"]: item["semantic_type"]
        for item in predicted_columns
    }

    total = 0
    correct = 0
    errors = []

    for col_name, expected_type in expected_mapping.items():
        total += 1
        predicted_type = predicted_map.get(col_name)

        if predicted_type == expected_type:
            correct += 1
        else:
            errors.append({
                "column_name": col_name,
                "expected": expected_type,
                "predicted": predicted_type,
            })

    return {
        "file_key": file_key,
        "status": "evaluated",
        "total": total,
        "correct": correct,
        "errors": errors,
    }


def main():
    all_results = []
    grand_total = 0
    grand_correct = 0

    print("=" * 60)
    print("FIELD ANALYSIS EVALUATION")
    print("=" * 60)

    for file_key, expected_mapping in EXPECTED_MAPPINGS.items():
        result = evaluate_one_file(file_key, expected_mapping)
        all_results.append(result)

        if result["status"] == "missing_output":
            print(f"\n[file] {file_key}")
            print("  Output file missing.")
            continue

        total = result["total"]
        correct = result["correct"]
        acc = correct / total if total > 0 else 0.0

        grand_total += total
        grand_correct += correct

        print(f"\n[file] {file_key}")
        print(f"  Correct: {correct}/{total}")
        print(f"  Accuracy: {acc:.2%}")

        if result["errors"]:
            print("  Errors:")
            for err in result["errors"]:
                print(
                    f"    - {err['column_name']}: "
                    f"expected={err['expected']}, predicted={err['predicted']}"
                )
        else:
            print("  Errors: none")

    overall_acc = grand_correct / grand_total if grand_total > 0 else 0.0

    print("\n" + "=" * 60)
    print("OVERALL SUMMARY")
    print("=" * 60)
    print(f"Total correct: {grand_correct}/{grand_total}")
    print(f"Overall accuracy: {overall_acc:.2%}")

    summary_output = {
        "total_correct": grand_correct,
        "total_fields": grand_total,
        "overall_accuracy": overall_acc,
        "per_file_results": all_results,
    }

    summary_path = OUTPUT_DIR / "evaluation_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_output, f, ensure_ascii=False, indent=2)

    print(f"\nSaved summary to: {summary_path}")


if __name__ == "__main__":
    main()