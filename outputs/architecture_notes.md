# Architecture Notes

## System Purpose

The data onboarding agent is designed to reduce the manual work required to standardize client CSV files into a unified analytics-ready schema.

The system receives two source files:

- customers CSV
- orders CSV

It produces five major outputs:

- field analysis
- unified schema recommendation
- mapping rules
- ETL config
- data dictionary

## High-Level Architecture

```text
Uploaded CSV files
        |
        v
FieldAnalyzer
        |
        v
SchemaRecommender
        |
        v
MappingGenerator
        |
        v
ETLConfigGenerator
        |
        v
DataDictionaryGenerator