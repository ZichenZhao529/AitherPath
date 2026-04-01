# src/mapping_generator.py

import json
from pathlib import Path
from openai import OpenAI

from src.mapping_prompts import (
    MAPPING_GENERATOR_SYSTEM_PROMPT,
    build_mapping_generator_user_prompt,
)


class MappingGenerator:
    def __init__(self, model: str = "gpt-5.4"):
        self.client = OpenAI()
        self.model = model

    def load_json_file(self, path: str | Path) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def generate_mapping(
        self,
        client_id: str,
        customer_analysis_path: str | Path,
        order_analysis_path: str | Path,
        unified_schema_path: str | Path,
    ) -> str:
        customer_analysis = self.load_json_file(customer_analysis_path)
        order_analysis = self.load_json_file(order_analysis_path)
        unified_schema = self.load_json_file(unified_schema_path)

        combined_field_analysis = {
            "client_id": client_id,
            "tables": [
                customer_analysis,
                order_analysis,
            ]
        }

        user_prompt = build_mapping_generator_user_prompt(
            client_id=client_id,
            field_analysis=combined_field_analysis,
            unified_schema=unified_schema,
        )

        response = self.client.responses.create(
            model=self.model,
            instructions=MAPPING_GENERATOR_SYSTEM_PROMPT,
            input=user_prompt,
        )

        return response.output_text