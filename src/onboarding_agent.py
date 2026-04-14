from pathlib import Path

from src.field_analyzer import FieldAnalyzer
from src.schema_recommender import SchemaRecommender
from src.mapping_generator import MappingGenerator
from src.etl_config_generator import ETLConfigGenerator
from src.data_dictionary_generator import DataDictionaryGenerator


class OnboardingAgent:
    def __init__(self):
        self.field_analyzer = FieldAnalyzer()
        self.schema_recommender = SchemaRecommender()
        self.mapping_generator = MappingGenerator()
        self.etl_config_generator = ETLConfigGenerator()
        self.data_dictionary_generator = DataDictionaryGenerator()

    def run(self, customer_csv, order_csv, client_name="unknown_client"):
        results = {
            "status": "success",
            "client_name": client_name,
            "results": {},
            "logs": [],
            "warnings": [],
            "errors": []
        }

        try:
            results["logs"].append("Step 1: Running field analysis...")
            field_analysis = self.field_analyzer.analyze(
                customer_csv=customer_csv,
                order_csv=order_csv,
                client_id=client_name
            )
            results["results"]["field_analysis"] = field_analysis
            #import json
            #print(json.dumps(field_analysis, indent=2, ensure_ascii=False))
            results["logs"].append("Field analysis completed.")
            results["logs"].append("Step 1b: Assessing data quality and risks...")
            warnings = self.assess_risks(field_analysis)
            results["warnings"] = warnings
            results["logs"].append("Risk assessment completed.")

            results["logs"].append("Step 2: Recommending unified schema...")
            schema = self.schema_recommender.recommend([field_analysis])
            results["results"]["schema_recommendation"] = schema
            results["logs"].append("Schema recommendation completed.")

            results["logs"].append("Step 3: Generating mapping rules...")
            mapping = self.mapping_generator.generate(
                client_id=client_name,
                field_analysis=field_analysis,
                schema=schema
            )
            results["results"]["mapping_rules"] = mapping
            results["logs"].append("Mapping generation completed.")

            results["logs"].append("Step 4: Generating ETL config...")
            etl_config = self.etl_config_generator.generate(mapping)
            results["results"]["etl_config"] = etl_config
            results["logs"].append("ETL config generation completed.")

            results["logs"].append("Step 5: Generating data dictionary...")
            data_dictionary = self.data_dictionary_generator.generate(
                schema_doc=schema,
                mapping_docs=[mapping]
            )
            results["results"]["data_dictionary"] = data_dictionary
            results["logs"].append("Data dictionary generation completed.")

        except Exception as e:
            results["status"] = "failed"
            results["errors"].append(str(e))
            results["logs"].append(f"Workflow failed: {str(e)}")

        return results
    
    def assess_risks(self, field_analysis: dict) -> list[dict]:
        warnings = []

        for table_result in field_analysis.get("tables", []):
            table_name = table_result.get("table_name", "unknown")

            columns = table_result.get("columns", [])
            raw_profiles = table_result.get("raw_profiles", [])

            # 先把 raw_profiles 做成字典，方便按 column_name 查 null_rate
            profile_map = {
                profile.get("column_name"): profile
                for profile in raw_profiles
            }

            for col in columns:
                field_name = col.get("column_name", "unknown")
                confidence = col.get("confidence")

                # 1. low-confidence warning
                if isinstance(confidence, str) and confidence.lower() in {"low", "medium"}:
                    warnings.append({
                        "type": "low_confidence_field",
                        "table": table_name,
                        "field": field_name,
                        "message": f"Low confidence detected for field '{field_name}' ({confidence})."
                    })

                # 2. high-null-rate warning
                profile = profile_map.get(field_name, {})
                null_rate = profile.get("null_rate")

                if null_rate is not None:
                    try:
                        null_rate_value = float(null_rate)
                        if null_rate_value > 0.3:
                            warnings.append({
                                "type": "high_null_rate",
                                "table": table_name,
                                "field": field_name,
                                "message": f"High null rate detected for field '{field_name}' ({null_rate_value:.0%})."
                            })
                    except (TypeError, ValueError):
                        pass

                # 3. optional: suspicious date-format warning
                semantic_type = col.get("semantic_type", "")
                sample_values = profile.get("sample_values", [])

                if semantic_type in {"registration_date", "order_date"}:
                    if len(sample_values) > 1:
                        separators = set()
                        for v in sample_values:
                            if isinstance(v, str):
                                if "-" in v:
                                    separators.add("-")
                                if "/" in v:
                                    separators.add("/")
                                if "." in v:
                                    separators.add(".")
                        if len(separators) > 1:
                            warnings.append({
                                "type": "inconsistent_date_format",
                                "table": table_name,
                                "field": field_name,
                                "message": f"Inconsistent date format detected for field '{field_name}'."
                            })

        return warnings