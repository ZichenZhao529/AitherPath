import json
from pathlib import Path

from src.field_analyzer import FieldAnalyzer

dataset_name = "client_b"
table_name = "customers"
csv_path = f"data/raw/{dataset_name}/{table_name}.csv"

analyzer = FieldAnalyzer(model="gpt-5.4")

result = analyzer.analyze_table(
    csv_path=csv_path,
    dataset_name=dataset_name,
    table_name=table_name,
)

output_dir = Path("outputs/field_analysis")
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / f"{dataset_name}_{table_name}.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"Saved to {output_file}")