from pathlib import Path
import json
import yaml


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"


def load_yaml(file_path: Path):
    with file_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(file_path: Path):
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def test_unified_schema_exists():
    schema_path = OUTPUTS_DIR / "schema" / "unified_schema.json"
    assert schema_path.exists()

    schema = load_json(schema_path)
    assert "unified_customers" in schema
    assert "unified_orders" in schema


def test_mapping_files_exist():
    for client_id in ["client_a", "client_b", "client_c"]:
        mapping_path = OUTPUTS_DIR / "mappings" / "generated" / f"{client_id}_mapping.yaml"
        assert mapping_path.exists()

        mapping_doc = load_yaml(mapping_path)
        assert mapping_doc["client_id"] == client_id
        assert "mappings" in mapping_doc
        assert len(mapping_doc["mappings"]) > 0


def test_etl_configs_exist():
    for client_id in ["client_a", "client_b", "client_c"]:
        etl_path = OUTPUTS_DIR / "etl_configs" / f"{client_id}_etl.yaml"
        assert etl_path.exists()

        etl_doc = load_yaml(etl_path)
        assert etl_doc["client_id"] == client_id
        assert "source" in etl_doc
        assert "schedule" in etl_doc
        assert "transformations" in etl_doc
        assert "destination" in etl_doc
        assert "quality_checks" in etl_doc


def test_data_dictionary_exists():
    dd_path = OUTPUTS_DIR / "data_dictionary.md"
    assert dd_path.exists()

    text = dd_path.read_text(encoding="utf-8")
    assert "# Unified Data Dictionary" in text
    assert "## unified_customers" in text
    assert "## unified_orders" in text


def test_validation_report_exists():
    report_path = OUTPUTS_DIR / "validation_report.json"
    assert report_path.exists()

    report = load_json(report_path)
    assert isinstance(report, list)
    assert len(report) >= 6

    for item in report:
        assert "table_name" in item
        assert "pass_rate" in item