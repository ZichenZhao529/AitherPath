from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"

def load_json(file_path: Path) -> List[Dict[str, Any]]:
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_yaml(file_path: Path) -> Any:
    with file_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

#需要可以压缩内部空格
def normalize_empty(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        cleaned = " ".join(value.strip().split())
        if cleaned == "":
            return None
        if cleaned.lower() in {"n/a", "null", "none", "unknown"}:
            return None
        return cleaned
    return value

def normalize_date(value: Any) -> Any:
    value = normalize_empty(value)
    if value is None:
        return None

    if not isinstance(value, str):
        return value

    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%m-%d-%Y",
        "%Y.%m.%d",
        "%d.%m.%Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None
#增加一个按client解析日期的函数
def normalize_date_by_source(value: Any, source_system: str) -> Any:
    value = normalize_empty(value)
    if value is None:
        return None

    if not isinstance(value, str):
        return value

    if source_system == "client_b":
        formats = [
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%Y.%m.%d",
            "%d.%m.%Y",
        ]
    elif source_system == "client_c":
        formats = [
            "%Y.%m.%d",
            "%d.%m.%Y",
            "%Y-%m-%d",
            "%Y/%m/%d",
        ]
    else:
        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%m-%d-%Y",
            "%d-%m-%Y",
            "%Y.%m.%d",
            "%d.%m.%Y",
        ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None

def to_float(value: Any) -> Optional[float]:
    value = normalize_empty(value)
    if value is None:
        return None
    try:
        return round(float(str(value).strip()), 2)
    except ValueError:
        return None


def split_name(full_name: Any) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Keep full_name, derive:
    - first_name = first token
    - last_name = all remaining tokens joined by space
    """
    full_name = normalize_empty(full_name)
    if full_name is None:
        return None, None, None

    parts = full_name.split()
    if len(parts) == 1:
        return full_name, parts[0], None

    return full_name, parts[0], " ".join(parts[1:])


def concat_names(first_name: Any, last_name: Any) -> Optional[str]:
    first_name = normalize_empty(first_name)
    last_name = normalize_empty(last_name)

    if first_name and last_name:
        return f"{first_name} {last_name}"
    if first_name:
        return first_name
    if last_name:
        return last_name
    return None


def normalize_phone(value: Any) -> Any:
    value = normalize_empty(value)
    if value is None:
        return None

    text = str(value).strip()
    if text.startswith("+"):
        return "+" + re.sub(r"[^0-9]", "", text[1:])
    return re.sub(r"[^0-9]", "", text)


def format_cleanup_by_target(target_field: str, value: Any) -> Any:
    value = normalize_empty(value)
    if value is None:
        return None

    if target_field == "phone":
        return normalize_phone(value)

    if target_field in {"country", "currency"}:
        return str(value).strip().upper()

    return str(value).strip()

#加一个status translation fallback dictionary
FALLBACK_STATUS_TRANSLATIONS = {
    "delivered": "delivered",
    "pending": "pending",
    "cancelled": "cancelled",
    "terkirim": "delivered",
    "menunggu": "pending",
    "dibatalkan": "cancelled",
    "geliefert": "delivered",
    "ausstehend": "pending",
    "storniert": "cancelled",
}

def parse_translation_rule(rule_value: Any) -> Dict[str, Any]:
    if isinstance(rule_value, dict):
        return rule_value

    if not isinstance(rule_value, str):
        return {}

    text = rule_value.strip()
    if not text:
        return {}

    result = {}

    for chunk in text.split(","):
        chunk = chunk.strip()
        if "->" not in chunk:
            continue

        left, right = chunk.split("->", 1)

        left = left.strip().strip("'\"")
        right = right.strip()

        # Stop at semicolon if explanatory text follows
        if ";" in right:
            right = right.split(";", 1)[0].strip()

        right = right.strip("'\"").rstrip(".")

        result[left] = right

    return result


def translate_value(value: Any, translation_rule: Any) -> Any:
    value = normalize_empty(value)
    if value is None:
        return None

    value_str = str(value).strip()
    mapping = parse_translation_rule(translation_rule)

    if value_str in mapping:
        return mapping[value_str]

    lower_map = {str(k).lower(): v for k, v in mapping.items()}
    if value_str.lower() in lower_map:
        return lower_map[value_str.lower()]

    if value_str.lower() in FALLBACK_STATUS_TRANSLATIONS:
        return FALLBACK_STATUS_TRANSLATIONS[value_str.lower()]

    return value_str.lower()

def extract_default_value(transformation_rule: Any) -> Any:
    if transformation_rule is None:
        return None

    text = str(transformation_rule).strip()

    # examples:
    # "city = null"
    # "currency = 'USD'"
    # "source_system = 'client_a'"
    if "=" in text:
        rhs = text.split("=", 1)[1].strip()
    else:
        rhs = text

    if rhs.lower() == "null":
        return None

    if (rhs.startswith("'") and rhs.endswith("'")) or (rhs.startswith('"') and rhs.endswith('"')):
        return rhs[1:-1]

    return rhs


def extract_prefix(transformation_rule: Any) -> str:
    if transformation_rule is None:
        return ""
    text = str(transformation_rule).strip()
    if text.lower().startswith("prefix:"):
        return text.split(":", 1)[1].strip()
    return text


def normalize_field_by_target(target_field: str, value: Any) -> Any:
    if target_field in {"registration_date", "order_date"}:
        return value

    if target_field in {"amount", "amount_usd"}:
        return to_float(value)

    if target_field in {"currency", "country"}:
        value = normalize_empty(value)
        if isinstance(value, str):
            return value.upper()
        return value

    if target_field == "order_status":
        value = normalize_empty(value)
        return str(value).strip().lower() if value is not None else None

    return normalize_empty(value)

def get_source_value(row: Dict[str, Any], field_name: Optional[str]) -> Any:
    if not field_name or field_name == "null":
        return None

    # support "Vorname, Nachname" style source_field by returning None here;
    # concatenation/calculated logic will handle it separately.
    if "," in str(field_name):
        return None

    return row.get(field_name)


def apply_splitting_rule(
    row: Dict[str, Any],
    rule: Dict[str, Any],
    transformed_so_far: Dict[str, Any]
) -> Any:
    source_field = rule.get("source_field")
    target_field = rule.get("target_field")
    source_value = get_source_value(row, source_field)

    full_name, first_name, last_name = split_name(source_value)

    if target_field == "full_name":
        return full_name
    if target_field == "first_name":
        return first_name
    if target_field == "last_name":
        return last_name

    return normalize_empty(source_value)


def apply_concatenation_rule(
    row: Dict[str, Any],
    rule: Dict[str, Any],
    transformed_so_far: Dict[str, Any]
) -> Any:
    target_field = rule.get("target_field")
    transformation_rule = str(rule.get("transformation_rule", "")).strip().lower()

    if target_field != "full_name":
        return None

    first_name = transformed_so_far.get("first_name")
    last_name = transformed_so_far.get("last_name")

    if first_name is None and "vorname" in transformation_rule:
        first_name = normalize_empty(row.get("Vorname"))
    if last_name is None and "nachname" in transformation_rule:
        last_name = normalize_empty(row.get("Nachname"))

    if first_name is None and "first_name" in transformation_rule:
        first_name = normalize_empty(row.get("first_name"))
    if last_name is None and "last_name" in transformation_rule:
        last_name = normalize_empty(row.get("last_name"))

    return concat_names(first_name, last_name)


def apply_calculated_field(
    row: Dict[str, Any],
    rule: Dict[str, Any],
    transformed_so_far: Dict[str, Any]
) -> Any:
    target_field = rule.get("target_field")

    if target_field == "full_name":
        return concat_names(
            transformed_so_far.get("first_name"),
            transformed_so_far.get("last_name"),
        )

    if target_field == "amount_usd":
        amount = transformed_so_far.get("amount")
        currency = transformed_so_far.get("currency")

        if amount is None:
            return None

        if currency == "USD":
            return round(float(amount), 2)

        
        return None

    return None


def apply_rule(
    row: Dict[str, Any],
    rule: Dict[str, Any],
    transformed_so_far: Dict[str, Any]
) -> Any:
    transform_type = str(rule.get("transform_type", "")).strip().lower()
    target_field = rule.get("target_field")
    source_field = rule.get("source_field")
    transformation_rule = rule.get("transformation_rule")

    source_value = get_source_value(row, source_field)

    if transform_type in {"direct_mapping", "renaming"}:
        return normalize_field_by_target(target_field, source_value)

    if transform_type == "format_cleanup":
        cleaned = format_cleanup_by_target(target_field, source_value)
        return normalize_field_by_target(target_field, cleaned)

    if transform_type == "date_format_conversion":
        source_system = transformed_so_far.get("source_system")
        if source_system is None:
            source_system = row.get("__source_system__")
        return normalize_date_by_source(source_value, source_system or "client_a")

    if transform_type == "value_translation":
        translated = translate_value(source_value, transformation_rule)
        return normalize_field_by_target(target_field, translated)

    if transform_type == "default_value":
        default_value = extract_default_value(transformation_rule)
        return normalize_field_by_target(target_field, default_value)

    if transform_type == "prefix_addition":
        value = normalize_empty(source_value)
        if value is None:
            return None
        prefix = extract_prefix(transformation_rule)
        return f"{prefix}{value}"

    if transform_type == "splitting":
        return apply_splitting_rule(row, rule, transformed_so_far)

    if transform_type == "concatenation":
        return apply_concatenation_rule(row, rule, transformed_so_far)

    if transform_type == "calculated_field":
        return apply_calculated_field(row, rule, transformed_so_far)

    return normalize_field_by_target(target_field, source_value)


def normalize_rules(raw_rules: Any) -> List[Dict[str, Any]]:
    if isinstance(raw_rules, list):
        return raw_rules

    if isinstance(raw_rules, dict):
        if isinstance(raw_rules.get("mappings"), list):
            return raw_rules["mappings"]
        if isinstance(raw_rules.get("rules"), list):
            return raw_rules["rules"]

    raise ValueError("Unsupported mapping YAML structure.")


def filter_rules_for_table(rules: List[Dict[str, Any]], table_name: str) -> List[Dict[str, Any]]:
    if table_name.endswith("_customers"):
        target_table = "unified_customers"
    elif table_name.endswith("_orders"):
        target_table = "unified_orders"
    else:
        raise ValueError(f"Cannot infer target table from {table_name}")

    return [rule for rule in rules if rule.get("target_table") == target_table]


def transform_row_with_rules(
    row: Dict[str, Any],
    rules: List[Dict[str, Any]],
    source_system: str
) -> Dict[str, Any]:
    transformed: Dict[str, Any] = {
        "source_system": source_system
    }

    row = dict(row)
    row["__source_system__"] = source_system

    for rule in rules:
        target_field = rule.get("target_field")
        if not target_field:
            continue
        transformed[target_field] = apply_rule(row, rule, transformed)

    transformed["source_system"] = source_system
    return transformed


def validate_business_rules(transformed: Dict[str, Any], table_name: str) -> List[Dict[str, str]]:
    errors: List[Dict[str, str]] = []

    if "orders" in table_name:
        amount = transformed.get("amount")
        if amount is not None and amount < 0:
            errors.append({
                "error_field": "amount",
                "error_type": "invalid_negative_amount",
                "error_message": "Order amount cannot be negative.",
            })

    return errors


def compare_dicts(actual: Dict[str, Any], expected: Dict[str, Any]) -> List[str]:
    mismatches = []

    for key, expected_value in expected.items():
        actual_value = actual.get(key)
        if actual_value != expected_value:
            mismatches.append(
                f"{key}: expected={expected_value!r}, actual={actual_value!r}"
            )

    return mismatches


def get_source_system_from_table_name(table_name: str) -> str:
    if table_name.startswith("client_a_"):
        return "client_a"
    if table_name.startswith("client_b_"):
        return "client_b"
    if table_name.startswith("client_c_"):
        return "client_c"
    raise ValueError(f"Unknown source system for table: {table_name}")



def get_validation_file(table_name: str) -> Path:
    return DATA_DIR / "validation_samples" / f"{table_name}_validation.json"

def get_mapping_file(table_name: str) -> Path:
    if table_name.startswith("client_a_"):
        client_name = "client_a"
    elif table_name.startswith("client_b_"):
        client_name = "client_b"
    elif table_name.startswith("client_c_"):
        client_name = "client_c"
    else:
        raise ValueError(f"Unknown client for table: {table_name}")


    generated_path = OUTPUTS_DIR / "mappings" / "generated" / f"{client_name}_mapping.yaml"

    if generated_path.exists():
        return generated_path

    raise FileNotFoundError(f"No mapping file found for {table_name} (client={client_name})")


def run_validation_for_table(table_name: str) -> Dict[str, Any]:
    validation_file = get_validation_file(table_name)
    mapping_file = get_mapping_file(table_name)
    source_system = get_source_system_from_table_name(table_name)

    samples = load_json(validation_file)
    raw_rules = load_yaml(mapping_file)
    rules = normalize_rules(raw_rules)
    rules = filter_rules_for_table(rules, table_name)

    total = 0
    passed = 0
    failed_cases: List[Dict[str, Any]] = []

    for sample in samples:
        total += 1
        sample_id = sample.get("sample_id", f"{table_name}_{total}")
        input_row = sample["input"]
        expected = sample.get("expected", {})
        validation_info = sample.get("validation", {})
        should_pass = validation_info.get("should_pass", True)

        actual = transform_row_with_rules(input_row, rules, source_system)
        errors = validate_business_rules(actual, table_name)

        if should_pass:
            if errors:
                failed_cases.append({
                    "sample_id": sample_id,
                    "reason": "Unexpected validation errors",
                    "actual_output": actual,
                    "errors": errors,
                })
                continue

            mismatches = compare_dicts(actual, expected)
            if mismatches:
                failed_cases.append({
                    "sample_id": sample_id,
                    "reason": "Output mismatch",
                    "actual_output": actual,
                    "expected_output": expected,
                    "mismatches": mismatches,
                })
            else:
                passed += 1

        else:
            if not errors:
                failed_cases.append({
                    "sample_id": sample_id,
                    "reason": "Expected validation failure but got none",
                    "actual_output": actual,
                    "expected_validation": validation_info,
                })
                continue

            expected_error_field = validation_info.get("error_field")
            expected_error_type = validation_info.get("error_type")

            matched = any(
                err.get("error_field") == expected_error_field
                and err.get("error_type") == expected_error_type
                for err in errors
            )

            if matched:
                passed += 1
            else:
                failed_cases.append({
                    "sample_id": sample_id,
                    "reason": "Validation error mismatch",
                    "actual_output": actual,
                    "expected_validation": validation_info,
                    "actual_errors": errors,
                })

    return {
        "table_name": table_name,
        "mapping_file": str(mapping_file),
        "validation_file": str(validation_file),
        "total_samples": total,
        "passed_samples": passed,
        "failed_samples": total - passed,
        "pass_rate": round((passed / total) * 100, 2) if total else 0.0,
        "failed_cases": failed_cases,
    }


def main() -> None:
    table_names = [
        "client_a_customers",
        "client_a_orders",
        "client_b_customers",
        "client_b_orders",
        "client_c_customers",
        "client_c_orders",
    ]

    all_results = []

    for table_name in table_names:
        try:
            result = run_validation_for_table(table_name)
            all_results.append(result)

            print(f"\n=== {table_name} ===")
            print(f"Mapping file: {result['mapping_file']}")
            print(f"Validation file: {result['validation_file']}")
            print(f"Total: {result['total_samples']}")
            print(f"Passed: {result['passed_samples']}")
            print(f"Failed: {result['failed_samples']}")
            print(f"Pass rate: {result['pass_rate']}%")

            if result["failed_cases"]:
                print("Failed cases:")
                for case in result["failed_cases"]:
                    print(json.dumps(case, ensure_ascii=False, indent=2))

        except Exception as e:
            print(f"\n=== {table_name} ===")
            print(f"Error: {e}")

    output_path = Path("outputs/validation_report.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f"\nSaved validation report to: {output_path}")


if __name__ == "__main__":
    main()




