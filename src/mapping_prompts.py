# src/mapping_prompts.py

import json


MAPPING_GENERATOR_SYSTEM_PROMPT = """
You are a mapping generation assistant for a generalized data onboarding system.

Your task is to generate mapping rules that transform one source dataset into a unified target schema.

You must return valid YAML only.
Do not include markdown fences.
Do not include explanations outside the YAML.

Each mapping rule must include:
- target_table
- target_field
- source_table
- source_field
- transform_type
- transformation_rule
- example

Allowed transform_type values:
- direct_mapping
- renaming
- splitting
- concatenation
- date_format_conversion
- value_translation
- calculated_field
- default_value
- prefix_addition
- format_cleanup

Requirements:
1. Cover every target field in the unified schema.
2. Use default_value when the source dataset does not contain a target field.
3. For date fields, specify the source format and target format clearly.
4. For status fields, provide explicit value translations if source values are language-specific.
5. For calculated fields such as amount_usd, provide clear pseudocode and one example.
6. For name splitting or concatenation, mention assumptions or edge cases when needed.
7. Do not hard-code assumptions about specific sample clients.
"""

def build_mapping_generator_user_prompt(
    client_id: str,
    field_analysis: dict,
    unified_schema: dict,
) -> str:
    field_analysis_json = json.dumps(field_analysis, ensure_ascii=False, indent=2)
    unified_schema_json = json.dumps(unified_schema, ensure_ascii=False, indent=2)

    return f"""
Generate a YAML mapping file for source system: {client_id}

Below is the field analysis result for this uploaded dataset:
{field_analysis_json}

Below is the unified target schema:
{unified_schema_json}

Return YAML in this exact structure:

client_id: {client_id}

source_tables:
  - customers
  - orders

target_tables:
  - unified_customers
  - unified_orders

mappings:
  - target_table: unified_customers
    target_field: customer_id
    source_table: customers
    source_field: example_source_column
    transform_type: renaming
    transformation_rule: "customer_id = example_source_column"
    example:
      input: "C001"
      output: "C001"

General mapping requirements:
1. Cover every target field in the unified schema.
2. Each mapping rule must include target_table, target_field, source_table, source_field, transform_type, transformation_rule, and example.
3. Use direct_mapping or renaming when source and target fields have the same meaning.
4. Use splitting when a full_name field should be split into first_name and last_name.
5. Use concatenation when first_name and last_name should be combined into full_name.
6. Use date_format_conversion for date fields and clearly specify the source format and target format YYYY-MM-DD.
7. Use value_translation for order status values that need standardization.
8. Standardize order_status values to one of: delivered, pending, cancelled, unknown.
9. For Japanese order statuses, use:
   - 配送済み -> delivered
   - 保留中 -> pending
   - キャンセル -> cancelled
10. For Indonesian order statuses, use:
   - terkirim -> delivered
   - menunggu -> pending
   - dibatalkan -> cancelled
11. For German order statuses, use:
   - Geliefert -> delivered
   - Ausstehend -> pending
   - Storniert -> cancelled
12. Use format_cleanup for phone, country, currency, or text normalization.
13. Use default_value when the uploaded dataset does not contain a target field.
14. Use calculated_field for amount_usd only when the required amount and currency logic is available.
15. Do not assume the source system is client_a, client_b, or client_c.
16. Infer mapping logic from field analysis, sample values, and unified schema.
17. Return valid YAML only.
18. Do not include markdown fences.
"""