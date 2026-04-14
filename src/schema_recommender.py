# src/schema_recommender.py

import json
from pathlib import Path
from openai import OpenAI

from src.schema_prompts import (
    SCHEMA_RECOMMENDER_SYSTEM_PROMPT,
    build_schema_recommender_user_prompt,
)


class SchemaRecommender:
    def __init__(self, model: str = "gpt-5.4"):
        self.client = OpenAI()
        self.model = model

    def load_field_analysis_file(self, path: str | Path) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_multiple_field_analyses(self, paths: list[str | Path]) -> list[dict]:
        results = []
        for path in paths:
            results.append(self.load_field_analysis_file(path))
        return results

    def recommend_schema(self, field_analysis_paths: list[str | Path]) -> dict:
        field_analysis_results = self.load_multiple_field_analyses(field_analysis_paths)
        user_prompt = build_schema_recommender_user_prompt(field_analysis_results)

        response = self.client.responses.create(
            model=self.model,
            instructions=SCHEMA_RECOMMENDER_SYSTEM_PROMPT,
            input=user_prompt,
        )

        return json.loads(response.output_text)

    def recommend(self, field_analysis_results: list[dict]) -> dict:
        user_prompt = build_schema_recommender_user_prompt(field_analysis_results)

        response = self.client.responses.create(
            model=self.model,
            instructions=SCHEMA_RECOMMENDER_SYSTEM_PROMPT,
            input=user_prompt,
        )

        return json.loads(response.output_text)