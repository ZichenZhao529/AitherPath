# src/run_schema_recommendation.py

import json
from pathlib import Path

from src.schema_recommender import SchemaRecommender


def main():
    input_paths = [
        "outputs/field_analysis/client_a_customers.json",
        "outputs/field_analysis/client_a_orders.json",
        "outputs/field_analysis/client_b_customers.json",
        "outputs/field_analysis/client_b_orders.json",
        "outputs/field_analysis/client_c_customers.json",
        "outputs/field_analysis/client_c_orders.json",
    ]

    recommender = SchemaRecommender(model="gpt-5.4")
    schema = recommender.recommend_schema(input_paths)

    output_dir = Path("outputs/schema")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "unified_schema.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)

    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()