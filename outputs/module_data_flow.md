# Module Data Flow

The current project data flow is:

Raw Source Data  
→ FieldAnalyzer  
→ SchemaRecommender  
→ unified_schema.json  
→ MappingGenerator  
→ client_a_mapping.yaml / client_b_mapping.yaml / client_c_mapping.yaml  
→ validate_mapping.py  
→ validation_report.json  
→ ETLConfigGenerator  
→ client_a_etl.yaml / client_b_etl.yaml / client_c_etl.yaml  
→ DataDictionaryGenerator  
→ data_dictionary.md

## Integration Notes
- `FieldAnalyzer` feeds source understanding into schema design.
- `SchemaRecommender` defines the unified target structure.
- `MappingGenerator` converts source fields into target-field mapping rules.
- `validate_mapping.py` verifies mapping correctness on sample rows.
- `ETLConfigGenerator` converts validated mappings into pipeline-ready ETL YAML.
- `DataDictionaryGenerator` converts schema + mapping into human-readable documentation.