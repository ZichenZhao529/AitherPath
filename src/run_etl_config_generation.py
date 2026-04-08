from pathlib import Path

from etl_config_generator import generate_etl_config


BASE_DIR = Path(__file__).resolve().parent.parent
MAPPINGS_DIR = BASE_DIR / "outputs" / "mappings" / "generated"
ETL_DIR = BASE_DIR / "outputs" / "etl_configs"


def main() -> None:
    jobs = [
        ("client_a_mapping.yaml", "client_a_etl.yaml"),
        ("client_b_mapping.yaml", "client_b_etl.yaml"),
        ("client_c_mapping.yaml", "client_c_etl.yaml"),
    ]

    for mapping_name, output_name in jobs:
        mapping_file = MAPPINGS_DIR / mapping_name
        output_file = ETL_DIR / output_name

        generate_etl_config(mapping_file, output_file)
        print(f"Generated: {output_file}")


if __name__ == "__main__":
    main()