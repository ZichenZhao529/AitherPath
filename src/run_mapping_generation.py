# src/run_mapping_generation.py

from pathlib import Path

from src.mapping_generator import MappingGenerator


def main():
    generator = MappingGenerator(model="gpt-5.4")
    unified_schema_path = "outputs/schema/unified_schema.json"

    jobs = [
        {
            "client_id": "client_a",
            "customer_analysis_path": "outputs/field_analysis/client_a_customers.json",
            "order_analysis_path": "outputs/field_analysis/client_a_orders.json",
        },
        {
            "client_id": "client_b",
            "customer_analysis_path": "outputs/field_analysis/client_b_customers.json",
            "order_analysis_path": "outputs/field_analysis/client_b_orders.json",
        },
        {
            "client_id": "client_c",
            "customer_analysis_path": "outputs/field_analysis/client_c_customers.json",
            "order_analysis_path": "outputs/field_analysis/client_c_orders.json",
        },
    ]

    output_dir = Path("outputs/mappings/generated")
    output_dir.mkdir(parents=True, exist_ok=True)

    for job in jobs:
        yaml_text = generator.generate_mapping(
            client_id=job["client_id"],
            customer_analysis_path=job["customer_analysis_path"],
            order_analysis_path=job["order_analysis_path"],
            unified_schema_path=unified_schema_path,
        )

        output_file = output_dir / f"{job['client_id']}_mapping.yaml"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(yaml_text)

        print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()