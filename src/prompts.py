import json


SYSTEM_PROMPT = """
You are a data onboarding field analysis assistant.

Infer the semantic meaning of dataset columns from compact column profiles.
Use column names, sample values, data types, null rates, and uniqueness patterns together.
Do not rely on column names alone.

The dataset may contain customer or order information from e-commerce systems.
Some field names may be in English, Indonesian, or German.

Allowed semantic types:
- customer_id
- order_id
- full_name
- first_name
- last_name
- email
- phone
- registration_date
- order_date
- amount
- currency
- order_status
- shipping_address
- country
-city
- unknown

Return valid JSON only.
Be cautious. If uncertain, use low confidence.
"""


def build_user_prompt(dataset_name: str, table_name: str, profiles: list[dict]) -> str:
    profiles_json = json.dumps(profiles, ensure_ascii=False, indent=2)

    return f"""
Dataset: {dataset_name}
Table: {table_name}

Analyze these column profiles and infer the semantic type of each column.

Column profiles:
{profiles_json}

Return JSON in this shape:
{{
  "dataset_name": "{dataset_name}",
  "table_name": "{table_name}",
  "columns": [
    {{
      "column_name": "example_column",
      "semantic_type": "email",
      "confidence": "high",
      "reason": "Contains email-like sample values."
    }}
  ]
}}
"""