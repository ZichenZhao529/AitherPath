import json
from pathlib import Path

import pandas as pd
from openai import OpenAI

from src.profiling import build_column_profiles
from src.prompts import SYSTEM_PROMPT, build_user_prompt


class FieldAnalyzer:
    def __init__(self, model: str = "gpt-5.4"):
        self.client = OpenAI()
        self.model = model

    def load_csv(self, csv_path: str | Path) -> pd.DataFrame:
        return pd.read_csv(csv_path, encoding="utf-8")
    
    def analyze_table(self, csv_path: str | Path, dataset_name: str, table_name: str) -> dict:
        df = self.load_csv(csv_path)
        profiles = build_column_profiles(df)

        user_prompt = build_user_prompt(
            dataset_name=dataset_name,
            table_name=table_name,
            profiles=profiles,
        )

        response = self.client.responses.create(
            model=self.model,
            instructions=SYSTEM_PROMPT,
            input=user_prompt,
        )

        text = response.output_text
        result = json.loads(text)
        result["raw_profiles"] = profiles
        return result
    
    def analyze(self, customer_csv: str | Path, order_csv: str | Path, client_id: str) -> dict:
        customer_result = self.analyze_table(customer_csv, client_id, "customers")
        order_result = self.analyze_table(order_csv, client_id, "orders")

        return {
            "client_id": client_id,
            "tables": [
                customer_result,
                order_result,
            ]
        }