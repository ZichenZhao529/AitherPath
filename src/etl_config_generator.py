from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"


def load_yaml(file_path: Path) -> Any:
    with file_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_rules(raw_rules: Any) -> List[Dict[str, Any]]:
    if isinstance(raw_rules, list):
        return raw_rules
    if isinstance(raw_rules, dict):
        if isinstance(raw_rules.get("mappings"), list):
            return raw_rules["mappings"]
        if isinstance(raw_rules.get("rules"), list):
            return raw_rules["rules"]
    raise ValueError("Unsupported mapping YAML structure.")


def get_source_tables(rules: List[Dict[str, Any]]) -> List[str]:
    tables = []
    for rule in rules:
        table = rule.get("source_table")
        if table and table not in tables:
            tables.append(table)
    return tables


def get_target_tables(rules: List[Dict[str, Any]]) -> List[str]:
    tables = []
    for rule in rules:
        table = rule.get("target_table")
        if table and table not in tables:
            tables.append(table)
    return tables


def build_transformation_step(rule: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "target_table": rule.get("target_table"),
        "target_field": rule.get("target_field"),
        "source_table": rule.get("source_table"),
        "source_field": rule.get("source_field"),
        "transform_type": rule.get("transform_type"),
        "transformation_rule": rule.get("transformation_rule"),
    }


def build_quality_checks(client_id: str) -> List[Dict[str, Any]]:
    checks = [
        {
            "check_type": "required_fields",
            "rules": {
                "unified_customers": ["customer_id", "full_name"],
                "unified_orders": ["order_id", "customer_id", "amount"],
            },
        },
        {
            "check_type": "date_format",
            "fields": ["registration_date", "order_date"],
            "expected_format": "YYYY-MM-DD",
        },
        {
            "check_type": "non_negative_amount",
            "table": "unified_orders",
            "field": "amount",
        },
    ]

    if client_id == "client_a":
        checks.append({
            "check_type": "default_currency_present",
            "table": "unified_orders",
            "field": "currency",
            "expected_value": "USD",
        })

    if client_id in {"client_b", "client_c"}:
        checks.append({
            "check_type": "currency_code_normalization",
            "table": "unified_orders",
            "field": "currency",
        })

    return checks


def build_etl_config(mapping_doc: Dict[str, Any]) -> Dict[str, Any]:
    client_id = mapping_doc.get("client_id")
    raw_rules = mapping_doc.get("mappings", [])
    rules = normalize_rules(raw_rules)

    source_tables = get_source_tables(rules)
    target_tables = get_target_tables(rules)

    config = {
        "client_id": client_id,
        "source": {
            "system": client_id,
            "tables": source_tables,
            "format": "csv",
        },
        "schedule": {
            "frequency": "daily",
            "trigger": "batch",
        },
        "transformations": group_transformations_by_source_table(rules),
        "destination": {
            "schema": "unified_schema",
            "tables": target_tables,
        },
        "quality_checks": build_quality_checks(client_id),
    }

    return config


def save_yaml(data: Dict[str, Any], file_path: Path) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def generate_etl_config(mapping_file: Path, output_file: Path) -> None:
    mapping_doc = load_yaml(mapping_file)
    etl_config = build_etl_config(mapping_doc)
    save_yaml(etl_config, output_file)

def group_transformations_by_source_table(rules: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}

    for rule in rules:
        source_table = rule.get("source_table", "unknown")
        if source_table not in grouped:
            grouped[source_table] = []

        grouped[source_table].append({
            "target_table": rule.get("target_table"),
            "target_field": rule.get("target_field"),
            "source_field": rule.get("source_field"),
            "transform_type": rule.get("transform_type"),
            "transformation_rule": rule.get("transformation_rule"),
        })

    return grouped