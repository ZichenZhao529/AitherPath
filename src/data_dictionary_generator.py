from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import yaml
    
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
SCHEMA_PATH = OUTPUTS_DIR / "schema" / "unified_schema.json"
MAPPINGS_DIR = OUTPUTS_DIR / "mappings" / "generated"


def load_json(file_path: Path) -> Any:
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_yaml(file_path: Path) -> Any:
    with file_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def collect_mapping_index(mapping_docs: List[Dict[str, Any]]) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    index: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}

    for doc in mapping_docs:
        client_id = doc.get("client_id")
        rules = doc.get("mappings", [])

        for rule in rules:
            target_table = rule.get("target_table")
            target_field = rule.get("target_field")

            if target_table not in index:
                index[target_table] = {}
            if target_field not in index[target_table]:
                index[target_table][target_field] = []

            index[target_table][target_field].append({
                "client_id": client_id,
                "source_table": rule.get("source_table"),
                "source_field": rule.get("source_field"),
                "transform_type": rule.get("transform_type"),
                "transformation_rule": rule.get("transformation_rule"),
            })

    return index


def format_field_section(
    table_name: str,
    field: Dict[str, Any],
    mapping_info: List[Dict[str, Any]],
) -> str:
    field_name = field.get("field_name")
    field_type = field.get("data_type")
    nullable = field.get("nullable")
    description = field.get("description", "No description provided.")

    lines = []
    lines.append(f"### {field_name}")
    lines.append(f"- **Type:** {field_type}")
    lines.append(f"- **Nullable:** {'Yes' if nullable else 'No'}")
    lines.append(f"- **Description:** {description}")

    source_coverage = field.get("source_coverage")
    if source_coverage:
        lines.append(f"- **Source coverage (schema):** {source_coverage}")

    design_reason = field.get("design_reason")
    if design_reason:
        lines.append(f"- **Design reason:** {design_reason}")

    if mapping_info:
        lines.append(f"- **Source mappings:**")
        for m in mapping_info:
            source_field = m.get("source_field")
            source_table = m.get("source_table")
            transform_type = m.get("transform_type")

            if source_field in [None, "null"]:
                source_label = "no direct source field"
            else:
                source_label = f"`{source_table}.{source_field}`"

            lines.append(
                f"  - {m['client_id']}: {source_label} via `{transform_type}`"
            )

        lines.append(f"- **Transformation notes:**")
        for m in mapping_info:
            lines.append(f"  - {m['client_id']}: {m['transformation_rule']}")

    lines.append("")
    return "\n".join(lines)


def build_data_dictionary(schema_doc: Dict[str, Any], mapping_index: Dict[str, Dict[str, List[Dict[str, Any]]]]) -> str:
    lines = []
    lines.append("# Unified Data Dictionary")
    lines.append("")
    lines.append("This document describes the unified dataset fields, their meanings, source coverage, and transformation logic.")
    lines.append("")

    for table_name, fields in schema_doc.items():
        lines.append(f"## {table_name}")
        lines.append("")

        for field in fields:
            field_name = field.get("field_name")
            mapping_info = mapping_index.get(table_name, {}).get(field_name, [])
            lines.append(format_field_section(table_name, field, mapping_info))

    return "\n".join(lines)

def save_markdown(content: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        f.write(content)


def generate_data_dictionary() -> Path:
    schema_doc = load_json(SCHEMA_PATH)

    mapping_docs = [
        load_yaml(MAPPINGS_DIR / "client_a_mapping.yaml"),
        load_yaml(MAPPINGS_DIR / "client_b_mapping.yaml"),
        load_yaml(MAPPINGS_DIR / "client_c_mapping.yaml"),
    ]

    mapping_index = collect_mapping_index(mapping_docs)
    content = build_data_dictionary(schema_doc, mapping_index)

    output_path = OUTPUTS_DIR / "data_dictionary.md"
    save_markdown(content, output_path)
    return output_path


class DataDictionaryGenerator:
    def generate(self, schema_doc: dict, mapping_docs: list[dict], output_path: Path | None = None) -> str:
        mapping_index = collect_mapping_index(mapping_docs)
        content = build_data_dictionary(schema_doc, mapping_index)

        if output_path is not None:
            save_markdown(content, output_path)

        return content