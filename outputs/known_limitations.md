# Known Limitations

## 1. LLM Output Variability

The system depends on LLM-generated JSON and YAML outputs. Although the prompts were refined to improve stability, outputs may still vary across runs.

This is a core limitation of LLM-backed workflows and would require stronger validation and structured output enforcement in a production version.

## 2. Limited Input Table Structure

The current app assumes that each client provides exactly two CSV files:

- customers
- orders

It does not yet support arbitrary numbers of tables or more complex relational schemas.

## 3. Limited Date Normalization

The system can reason about different date formats in mapping rules, but the transformation layer does not yet support every international date format.

For example, Japanese-style dates such as `2024年01月15日` may require additional parsing logic.

## 4. Limited Currency Conversion

The system can preserve currency fields and generate `amount_usd` mapping logic, but real exchange-rate conversion is not implemented.

In a production system, this would require an exchange-rate table or external currency conversion service.

## 5. No Human-in-the-Loop Editing Yet

The current Streamlit app displays generated mappings but does not allow users to edit and approve mapping rules directly in the interface.

A production onboarding tool should allow users to review, modify, approve, and version mappings.

## 6. Limited Business Rule Validation

The validation logic currently checks some simple conditions, such as non-negative amounts. It does not yet validate deeper business rules, such as whether every order customer ID exists in the customer table.

## 7. Synthetic Test Data

The current project uses synthetic client datasets. This is useful for controlled testing, but real client data would likely include more noise, missing values, unusual encodings, inconsistent schemas, and sensitive data concerns.

## 8. Privacy and Security

The prototype sends compact column profiles and sample values to an LLM. For production use, sensitive fields should be masked, minimized, or processed under strict privacy controls.