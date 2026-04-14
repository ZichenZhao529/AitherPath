import streamlit as st
import pandas as pd
import tempfile
from pathlib import Path
import yaml
import json

from src.onboarding_agent import OnboardingAgent

st.set_page_config(page_title="Data Onboarding Agent", layout="wide")

st.title("Data Onboarding Agent Demo")
st.write("Upload customer and order CSV files, preview the data, and run the onboarding workflow.")

if "onboarding_result" not in st.session_state:
    st.session_state["onboarding_result"] = None

st.sidebar.header("Inputs")
client_name = st.sidebar.selectbox(
    "Select Client",
    ["client_a", "client_b", "client_c"]
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

col1, col2 = st.columns(2)

with col1:
    st.subheader("Customers Preview")
    if customer_file is not None:
        customer_df = pd.read_csv(customer_file)
        st.dataframe(customer_df.head())
        st.caption(f"Shape: {customer_df.shape}")
    else:
        st.info("Please upload a customers CSV file.")

with col2:
    st.subheader("Orders Preview")
    if order_file is not None:
        order_df = pd.read_csv(order_file)
        st.dataframe(order_df.head())
        st.caption(f"Shape: {order_df.shape}")
    else:
        st.info("Please upload an orders CSV file.")

if st.button("Run Onboarding Agent"):
    if customer_file is None or order_file is None:
        st.error("Please upload both customers and orders CSV files.")
    else:
        try:
            with st.spinner("Running onboarding workflow..."):
                agent = OnboardingAgent()

                with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_customer:
                    tmp_customer.write(customer_file.getvalue())
                    customer_path = Path(tmp_customer.name)

                with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_order:
                    tmp_order.write(order_file.getvalue())
                    order_path = Path(tmp_order.name)

                result = agent.run(
                    customer_csv=customer_path,
                    order_csv=order_path,
                    client_name=client_name
                )

                st.session_state["onboarding_result"] = result

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
        st.write(f"**Status:** {result['status']}")
        st.write(f"**Client:** {result['client_name']}")

        st.subheader("Warnings")
        if result["warnings"]:
            for w in result["warnings"]:
                st.warning(w["message"])
        else:
            st.success("No warnings detected.")

        st.subheader("Logs")
        for log in result["logs"]:
            st.text(log)

    with tabs[1]:
        st.subheader("Field Analysis")
        st.json(result["results"].get("field_analysis", {}))

    with tabs[2]:
        st.subheader("Schema Recommendation")
        schema_data = result["results"].get("schema_recommendation", {})

        st.json(schema_data)

        schema_json = json.dumps(schema_data, indent=2, ensure_ascii=False)
        st.download_button(
            label="Download Schema JSON",
            data=schema_json,
            file_name=f"{result['client_name']}_schema.json",
            mime="application/json"
        )

    with tabs[3]:
        st.subheader("Mapping Rules")
        mapping_data = result["results"].get("mapping_rules", {})

        st.json(mapping_data)

        mapping_yaml = yaml.safe_dump(mapping_data, sort_keys=False, allow_unicode=True)
        st.download_button(
            label="Download Mapping YAML",
            data=mapping_yaml,
            file_name=f"{result['client_name']}_mapping.yaml",
            mime="text/yaml"
        )

    with tabs[4]:
        st.subheader("ETL Config")
        etl_data = result["results"].get("etl_config", {})

        st.json(etl_data)

        etl_yaml = yaml.safe_dump(etl_data, sort_keys=False, allow_unicode=True)
        st.download_button(
            label="Download ETL Config YAML",
            data=etl_yaml,
            file_name=f"{result['client_name']}_etl_config.yaml",
            mime="text/yaml"
        )

    with tabs[5]:
        st.subheader("Data Dictionary")
        data_dictionary = result["results"].get("data_dictionary", "")

        st.text(data_dictionary if data_dictionary else "No data dictionary available.")

        st.download_button(
            label="Download Data Dictionary",
            data=data_dictionary,
            file_name=f"{result['client_name']}_data_dictionary.md",
            mime="text/markdown"
        )