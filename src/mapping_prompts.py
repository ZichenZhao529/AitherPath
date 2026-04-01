# src/mapping_prompts.py

import json


MAPPING_GENERATOR_SYSTEM_PROMPT = """
You are a mapping generation assistant for a data onboarding system.

Your task is to generate mapping rules that transform one client's source fields
into a unified target schema.

You must return valid YAML only.

Each mapping rule must include:
- target_table
- target_field
- source_table
- source_field
- transform_type
- transformation_rule
- example

Optional:
- notes

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
2. Use default_value when the source client does not contain a target field.
3. For date fields, specify the source format and target format clearly.
4. For status fields, provide explicit value translations if source values are language-specific.
5. For calculated fields such as amount_usd, provide clear pseudocode and one example.
6. For name splitting or concatenation, mention assumptions or edge cases when needed.
"""


def build_mapping_generator_user_prompt(
    client_id: str,
    field_analysis: dict,
    unified_schema: dict,
) -> str:
    field_analysis_json = json.dumps(field_analysis, ensure_ascii=False, indent=2)
    unified_schema_json = json.dumps(unified_schema, ensure_ascii=False, indent=2)

    return f"""
Generate a YAML mapping file for client: {client_id}

Below is the field analysis result for this client:
{field_analysis_json}

Below is the unified target schema:
{unified_schema_json}

Return YAML in this structure:

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
    source_field: cust_id
    transform_type: renaming
    transformation_rule: "customer_id = cust_id"
    example:
      input: "C001"
      output: "C001"
     
For client_a:
- If only `full_name` is available, split it into `first_name` and `last_name` using a simple space-based rule.
- Assume the default currency is `USD` when no explicit currency field is provided.
- Therefore, map `amount_usd` directly from `total_amt`.

For client_b:
- If only `nama` is available, split it into `first_name` and `last_name` using a simple space-based rule.
- Translate `status_pesanan` into the standardized target vocabulary:
  - `terkirim` -> `delivered`
  - `menunggu` -> `pending`
  - `dibatalkan` -> `cancelled`
- Do not leave `first_name` or `last_name` as null when a simple split from `nama` is possible.

For client_c:
- Normalize `Telefon` into the project’s standard phone format instead of keeping the raw source formatting.
- Normalize `Land` and `Währung` using trimming and uppercase formatting when appropriate.
- Translate German order statuses into the standardized target vocabulary:
  - `Geliefert` -> `delivered`
  - `Ausstehend` -> `pending`
  - `Storniert` -> `cancelled`
- Use `cancelled` rather than `canceled` to stay consistent with the project vocabulary.
- Use `delivered` rather than `shipped` for the standardized completed-order status.
Make sure every target field in unified_customers and unified_orders is covered.
"""