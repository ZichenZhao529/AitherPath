# Module Interface Specification

This document defines the input/output contract for the main Week 1–4 modules so they can be integrated more reliably in Week 5.

## 1. FieldAnalyzer
**Purpose:** Analyze raw source fields and summarize data characteristics.

**Input:**
- Source sample rows or source schema metadata
- Client identifier
- Source table name

**Output:**
- Structured field analysis result
- Suggested field types
- Data quality observations
- Candidate mapping hints

**Expected format:**
- Python dict or JSON-like object

---

## 2. SchemaRecommender
**Purpose:** Generate or refine the unified schema from source analysis outputs.

**Input:**
- Field analysis results
- Cross-client comparison results
- Design constraints for unified schema

**Output:**
- Unified schema JSON

**Expected format:**
- File: `unified_schema.json`
- Top-level structure:
  - `unified_customers`
  - `unified_orders`

---

## 3. MappingGenerator
**Purpose:** Generate client-specific mapping YAML from source fields into unified schema.

**Input:**
- Unified schema
- Source field information
- Client identifier
- Table-level source metadata

**Output:**
- Client-specific mapping YAML

**Expected format:**
- File: `<client_id>_mapping.yaml`
- Contains:
  - `client_id`
  - `mappings`
  - `target_table`
  - `target_field`
  - `source_table`
  - `source_field`
  - `transform_type`
  - `transformation_rule`

---

## 4. ETLConfigGenerator
**Purpose:** Convert validated mapping rules into ETL pipeline configuration.

**Input:**
- Validated mapping YAML
- Unified schema
- Client identifier

**Output:**
- Client-specific ETL YAML

**Expected format:**
- File: `<client_id>_etl.yaml`
- Contains:
  - `source`
  - `schedule`
  - `transformations`
  - `destination`
  - `quality_checks`

---

## 5. DataDictionaryGenerator
**Purpose:** Generate human-readable documentation for unified tables and fields.

**Input:**
- Unified schema JSON
- Client mapping YAML files

**Output:**
- Markdown data dictionary

**Expected format:**
- File: `data_dictionary.md`
- Covers:
  - field type
  - nullability
  - description
  - source coverage
  - design reason
  - source mappings
  - transformation notes