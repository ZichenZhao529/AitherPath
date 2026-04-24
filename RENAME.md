# Data Onboarding Agent

## Project Overview

This project is a data onboarding assistant that helps standardize client CSV datasets into a unified schema. The system is designed for situations where different clients provide similar business data using different column names, languages, formats, and structures.

Instead of manually writing mapping rules for each client, the agent uses LLM-assisted reasoning to:

1. Analyze source CSV fields
2. Recommend a unified schema
3. Generate mapping rules
4. Create an ETL configuration
5. Produce a data dictionary
6. Surface data quality warnings

The project was originally tested on three synthetic clients and later extended with a fourth unseen client to evaluate generalization.

## Problem

In real onboarding workflows, different clients often provide data in inconsistent formats. For example, one client may use `cust_id`, another may use `id_pelanggan`, and another may use `Kundennummer` for the same customer identifier concept.

This creates a manual and repetitive mapping problem. Analysts or engineers need to understand each client’s data, infer field meanings, define transformations, and document the final schema.

This project automates part of that workflow.

## Main Workflow

The Streamlit app allows users to upload two CSV files:

- `customers.csv`
- `orders.csv`

After upload, the system runs the full onboarding workflow:

1. Field analysis
2. Data quality and risk assessment
3. Unified schema recommendation
4. Mapping rule generation
5. ETL config generation
6. Data dictionary generation

## Project Structure

```text
AitherPath/
├── app.py
├── README.md
├── data/
│   ├── raw/
│   │   ├── client_a/
│   │   ├── client_b/
│   │   ├── client_c/
│   │   └── client_d/
│   └── validation_samples/
├── outputs/
│   ├── field_analysis/
│   ├── mappings/
│   ├── schema/
│   ├── etl_configs/
│   ├── data_dictionary.md
│   ├── generalization_test_report.md
│   ├── edge_case_handling_report.md
│   └── prompt_stability_report.md
├── src/
│   ├── field_analyzer.py
│   ├── schema_recommender.py
│   ├── mapping_generator.py
│   ├── etl_config_generator.py
│   ├── data_dictionary_generator.py
│   ├── onboarding_agent.py
│   ├── profiling.py
│   ├── prompts.py
│   ├── schema_prompts.py
│   └── mapping_prompts.py
└── test_client_d.py