# Future Improvements

## 1. Support More Input Tables

The current workflow supports two source tables: customers and orders. A future version could allow users to upload any number of source tables and automatically infer relationships among them.

## 2. Add Human-in-the-Loop Mapping Review

The app could include an editable mapping interface where users can review, change, approve, and save generated mapping rules.

This would make the system more reliable and practical for real onboarding workflows.

## 3. Add Stronger Structured Output Validation

Future versions could validate every generated JSON and YAML output against a formal schema. If the LLM output is invalid, the system could automatically retry with a correction prompt.

## 4. Improve Date Parsing

The transformation layer could support more international date formats, including Japanese, European, American, and mixed-format dates.

## 5. Add Currency Conversion

The system could use an exchange-rate table or external API to convert source amounts into normalized USD values.

## 6. Add Referential Integrity Checks

The system could check whether order-level customer IDs exist in the customer table and surface broken foreign-key relationships.

## 7. Add PII Masking

Before sending profiles or sample values to the LLM, the system could mask sensitive information such as names, emails, phone numbers, and addresses.

## 8. Export Executable ETL Code

The current system generates mapping rules and ETL configuration. A future version could generate executable Python, SQL, or dbt transformation scripts.

## 9. Add Versioning

Generated schemas, mappings, and ETL configs could be versioned so that teams can compare changes across onboarding runs.

## 10. Connect to Real Data Sources

Instead of only uploading CSV files, the system could connect to cloud storage, databases, or data warehouses.