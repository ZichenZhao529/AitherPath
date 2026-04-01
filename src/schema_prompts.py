# src/schema_prompts.py

import json


SCHEMA_RECOMMENDER_SYSTEM_PROMPT = """
You are a schema recommendation assistant for a data onboarding system.

Your task is to recommend a unified target schema based on field analysis results from multiple client datasets.

You must recommend exactly two target tables:
1. unified_customers
2. unified_orders

Place only customer-level attributes in unified_customers, such as:
customer_id, names, email, phone, registration_date, city, country, source_system.

Place only order-level attributes in unified_orders, such as:
order_id, customer_id, order_date, amount, currency, amount_usd, order_status, shipping_address, source_system.

Do not mix customer profile fields into the orders table.
Do not mix transaction fields into the customers table.

For each target field, return:
- field_name
- data_type
- nullable
- description
- source_coverage
- design_reason

Important design choices to handle explicitly:
- whether names should remain as full_name or also include first_name and last_name
- whether geography should include city and country
- whether monetary values should preserve original currency and also include normalized USD

If some clients do not contain a target field, state that clearly in source_coverage or design_reason.

Return valid JSON only.
"""


def build_schema_recommender_user_prompt(field_analysis_results: list[dict]) -> str:
    compact_input = []

    for item in field_analysis_results:
        compact_input.append({
            "dataset_name": item.get("dataset_name"),
            "table_name": item.get("table_name"),
            "columns": item.get("columns", []),
        })

    payload = json.dumps(compact_input, ensure_ascii=False, indent=2)

    return f"""
Below are field analysis results from multiple client datasets.

Use them to recommend a unified target schema with exactly two target tables:
- unified_customers
- unified_orders

Field analysis results:
{payload}

Return JSON in this format:
{{
  "unified_customers": [
    {{
      "field_name": "customer_id",
      "data_type": "string",
      "nullable": false,
      "description": "Unified customer identifier",
      "source_coverage": "A, B, C",
      "design_reason": "Core primary key for customer-level integration"
    }}
  ],
  "unified_orders": [
    {{
      "field_name": "order_id",
      "data_type": "string",
      "nullable": false,
      "description": "Unified order identifier",
      "source_coverage": "A, B, C",
      "design_reason": "Core primary key for order-level integration"
    }}
  ]
}}
"""