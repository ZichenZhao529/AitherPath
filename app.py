import streamlit as st
import pandas as pd
import tempfile
from pathlib import Path
import yaml
import json

from src.onboarding_agent import OnboardingAgent


st.set_page_config(page_title="Data Onboarding Agent", layout="wide")

st.title("Data Onboarding Agent Demo")
st.write(
    "Upload customer and order CSV files, preview the data, and run the onboarding workflow."
)


if "onboarding_result" not in st.session_state:
    st.session_state["onboarding_result"] = None


def validate_uploaded_csv(uploaded_file, file_label, max_rows=10000):
    """
    Validate uploaded CSV before running the onboarding workflow.
    """
    if uploaded_file is None:
        return None, f"Please upload a {file_label} CSV file.", None

    try:
        df = pd.read_csv(uploaded_file)
        uploaded_file.seek(0)
    except pd.errors.EmptyDataError:
        return None, f"{file_label} file is empty. Please upload a valid CSV with headers and rows.", None
    except UnicodeDecodeError:
        return None, f"{file_label} file encoding is not supported. Please save it as UTF-8 CSV and upload again.", None
    except Exception as e:
        return None, f"Could not read {file_label} file: {e}", None

    if df.shape[1] == 0:
        return None, f"{file_label} file has no columns.", None

    if df.shape[0] == 0:
        return None, f"{file_label} file only contains headers but no data rows.", None

    unnamed_cols = [
        col for col in df.columns
        if str(col).strip().lower().startswith("unnamed")
    ]

    if len(unnamed_cols) == len(df.columns):
        return None, f"{file_label} file has only unnamed columns. Please check the header row.", None

    warning = None

    unclear_cols = []
    for col in df.columns:
        col_text = str(col).strip().lower()
        if col_text in {"", "unknown", "na", "n/a", "none", "null"}:
            unclear_cols.append(col)

    if unclear_cols:
        warning = (
            f"{file_label} file contains unclear column names: {unclear_cols}. "
            "The agent may return lower-confidence mappings."
        )

    if df.shape[0] > max_rows:
        df = df.head(max_rows)
        warning = (
            f"{file_label} file is large. Only the first {max_rows} rows "
            "will be used for analysis."
        )

    return df, None, warning


def save_dataframe_to_temp_csv(df):
    """
    Save dataframe to a temporary CSV path.
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    temp_path = Path(temp_file.name)
    temp_file.close()

    df.to_csv(temp_path, index=False)
    return temp_path


st.sidebar.header("Inputs")

client_name = st.sidebar.text_input(
    "Optional source name",
    value="uploaded_client"
)

customer_file = st.sidebar.file_uploader(
    "Upload customers CSV",
    type=["csv"],
    key="customer_csv"
)

order_file = st.sidebar.file_uploader(
    "Upload orders CSV",
    type=["csv"],
    key="order_csv"
)

run_button = st.sidebar.button("Run Onboarding Agent")


col1, col2 = st.columns(2)

customer_df = None
customer_error = None
customer_warning = None

order_df = None
order_error = None
order_warning = None


with col1:
    st.subheader("Customers Preview")

    if customer_file is not None:
        customer_df, customer_error, customer_warning = validate_uploaded_csv(
            customer_file,
            "customers"
        )

        if customer_error:
            st.error(customer_error)
        else:
            st.dataframe(customer_df.head(), use_container_width=True)
            st.caption(f"Shape: {customer_df.shape}")

            if customer_warning:
                st.warning(customer_warning)
    else:
        st.info("Please upload a customers CSV file.")


with col2:
    st.subheader("Orders Preview")

    if order_file is not None:
        order_df, order_error, order_warning = validate_uploaded_csv(
            order_file,
            "orders"
        )

        if order_error:
            st.error(order_error)
        else:
            st.dataframe(order_df.head(), use_container_width=True)
            st.caption(f"Shape: {order_df.shape}")

            if order_warning:
                st.warning(order_warning)
    else:
        st.info("Please upload an orders CSV file.")


if run_button:
    if customer_file is None or order_file is None:
        st.error("Please upload both customers and orders CSV files.")
    else:
        customer_df, customer_error, customer_warning = validate_uploaded_csv(
            customer_file,
            "customers"
        )
        order_df, order_error, order_warning = validate_uploaded_csv(
            order_file,
            "orders"
        )

        if customer_error or order_error:
            if customer_error:
                st.error(customer_error)
            if order_error:
                st.error(order_error)
        else:
            try:
                with st.spinner("Running onboarding workflow..."):
                    customer_path = save_dataframe_to_temp_csv(customer_df)
                    order_path = save_dataframe_to_temp_csv(order_df)

                    agent = OnboardingAgent()

                    result = agent.run(
                        customer_csv=customer_path,
                        order_csv=order_path,
                        client_name=client_name
                    )

                    st.session_state["onboarding_result"] = result

                if result["status"] == "success":
                    st.success("Onboarding workflow completed successfully.")
                else:
                    st.error("Onboarding workflow failed. Please check the errors below.")

            except Exception as e:
                st.error(f"App error: {e}")


if st.session_state["onboarding_result"] is not None:
    result = st.session_state["onboarding_result"]

    tabs = st.tabs([
        "Summary",
        "Field Analysis",
        "Schema",
        "Mapping",
        "ETL Config",
        "Data Dictionary"
    ])

    with tabs[0]:
        st.subheader("Run Summary")
        st.write(f"**Status:** {result.get('status')}")
        st.write(f"**Source:** {result.get('client_name')}")

        st.subheader("Warnings")
        if result.get("warnings"):
            for w in result["warnings"]:
                if isinstance(w, dict):
                    st.warning(w.get("message", str(w)))
                else:
                    st.warning(str(w))
        else:
            st.success("No warnings detected.")

        st.subheader("Logs")
        for log in result.get("logs", []):
            st.text(log)

        if result.get("errors"):
            st.subheader("Errors")
            for error in result["errors"]:
                st.error(error)

    with tabs[1]:
        st.subheader("Field Analysis")
        field_analysis = result.get("results", {}).get("field_analysis", {})
        st.json(field_analysis)

        field_analysis_json = json.dumps(
            field_analysis,
            indent=2,
            ensure_ascii=False
        )

        st.download_button(
            label="Download Field Analysis JSON",
            data=field_analysis_json,
            file_name=f"{result.get('client_name', 'uploaded_client')}_field_analysis.json",
            mime="application/json"
        )

    with tabs[2]:
        st.subheader("Schema Recommendation")
        schema_data = result.get("results", {}).get("schema_recommendation", {})
        st.json(schema_data)

        schema_json = json.dumps(
            schema_data,
            indent=2,
            ensure_ascii=False
        )

        st.download_button(
            label="Download Schema JSON",
            data=schema_json,
            file_name=f"{result.get('client_name', 'uploaded_client')}_schema.json",
            mime="application/json"
        )

    with tabs[3]:
        st.subheader("Mapping Rules")
        mapping_data = result.get("results", {}).get("mapping_rules", {})
        st.json(mapping_data)

        mapping_yaml = yaml.safe_dump(
            mapping_data,
            sort_keys=False,
            allow_unicode=True
        )

        st.download_button(
            label="Download Mapping YAML",
            data=mapping_yaml,
            file_name=f"{result.get('client_name', 'uploaded_client')}_mapping.yaml",
            mime="text/yaml"
        )

    with tabs[4]:
        st.subheader("ETL Config")
        etl_data = result.get("results", {}).get("etl_config", {})
        st.json(etl_data)

        etl_yaml = yaml.safe_dump(
            etl_data,
            sort_keys=False,
            allow_unicode=True
        )

        st.download_button(
            label="Download ETL Config YAML",
            data=etl_yaml,
            file_name=f"{result.get('client_name', 'uploaded_client')}_etl_config.yaml",
            mime="text/yaml"
        )

    with tabs[5]:
        st.subheader("Data Dictionary")
        data_dictionary = result.get("results", {}).get("data_dictionary", "")

        if data_dictionary:
            st.markdown(data_dictionary)
        else:
            st.info("No data dictionary available.")

        st.download_button(
            label="Download Data Dictionary",
            data=data_dictionary,
            file_name=f"{result.get('client_name', 'uploaded_client')}_data_dictionary.md",
            mime="text/markdown"
        )