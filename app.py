from pathlib import Path
import sys
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
RAW_DIR = ROOT / "data" / "raw"
UPLOAD_DIR = ROOT / "data" / "uploads"
REPORT_DIR = ROOT / "reports"
PROCESSED_DIR = ROOT / "data" / "processed"
CHART_DIR = ROOT / "visualizations"

st.set_page_config(page_title="Sales Intelligence Dashboard", page_icon="📊", layout="wide")
st.markdown("# 📊 Sales Intelligence Dashboard")
st.caption("Enterprise Sales Data Processing & Business Intelligence Automation")

PAGES = ["Dashboard", "Upload Sales CSV", "Cleaned Data", "Rejected Records",
         "Anomaly Detection", "Business Analytics", "Charts", "Management Report"]
with st.sidebar:
    st.header("Navigation")
    page = st.radio("Choose a page", PAGES)
    st.divider()
    st.caption("Upload a CSV and click Run Sales Analysis. Uploaded data is processed separately from sample CSVs.")
    st.caption("Current analysis source:")
    st.write(st.session_state.get("active_source", "Bundled sample data / latest pipeline run"))

def read_csv_safe(path):
    try:
        if path.exists() and path.stat().st_size:
            return pd.read_csv(path)
    except Exception as exc:
        st.warning(f"Could not read {path.name}: {exc}")
    return pd.DataFrame()

def required_columns():
    from src.data_loader import REQUIRED_COLUMNS
    return REQUIRED_COLUMNS

def run_uploaded_analysis(df, filename):
    try:
        from src.pipeline import run_pipeline
        with st.spinner("Validating and processing the uploaded dataset..."):
            run_pipeline(input_df=df, source_name=filename)
        st.session_state["active_source"] = filename
        st.session_state["active_run_id"] = f"{filename}:{len(df)}"
        st.success(f"Analysis completed for {filename}. Processed {len(df)} uploaded rows without combining sample CSVs.")
        st.rerun()
    except Exception as exc:
        st.error(f"Analysis failed: {exc}")
        st.info("Check the required columns and processing.log for details.")

def download_df(label, df, filename):
    st.download_button(label, df.to_csv(index=False).encode("utf-8-sig"),
                       file_name=filename, mime="text/csv", disabled=df.empty)

if page == "Upload Sales CSV":
    st.subheader("Upload Sales Data")
    st.write("Choose one CSV file. It will be processed by itself and will not be combined with January/February sample files.")
    uploaded = st.file_uploader("Choose a sales CSV file", type=["csv"], key="sales_csv_upload")
    if uploaded is not None:
        try:
            uploaded.seek(0)
            preview = pd.read_csv(uploaded)
            preview.columns = [str(c).strip() for c in preview.columns]
            missing = [c for c in required_columns() if c not in preview.columns]
            st.write(f"**Preview:** {len(preview)} rows × {len(preview.columns)} columns")
            st.dataframe(preview.head(10), use_container_width=True)
            if missing:
                st.error("Required columns missing: " + ", ".join(missing))
                st.caption("Expected columns: " + ", ".join(required_columns()))
            elif st.button("▶ Run Sales Analysis", type="primary"):
                UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
                safe_name = Path(uploaded.name).name
                (UPLOAD_DIR / safe_name).write_bytes(uploaded.getvalue())
                run_uploaded_analysis(preview, safe_name)
        except Exception as exc:
            st.error(f"CSV open/validation error: {exc}")
    st.info("Required fields are checked before processing. Invalid transactions are preserved in Rejected Records with reasons.")

elif page == "Dashboard":
    st.subheader("Business Overview")
    kpis = read_csv_safe(REPORT_DIR / "sales_kpis.csv")
    if not kpis.empty:
        k = kpis.iloc[0].to_dict()
        metrics = [
            ("Total Revenue", f"₹{float(k.get('Total_Revenue', 0)):,.2f}"),
            ("Total Orders", f"{int(float(k.get('Total_Orders', 0))):,}"),
            ("Total Customers", f"{int(float(k.get('Total_Customers', 0))):,}"),
            ("Units Sold", f"{int(float(k.get('Units_Sold', 0))):,}"),
            ("Clean Records", str(len(read_csv_safe(PROCESSED_DIR / 'cleaned_sales.csv')))),
            ("Rejected Records", str(len(read_csv_safe(PROCESSED_DIR / 'rejected_records.csv')))),
            ("Anomaly Flags", str(len(read_csv_safe(PROCESSED_DIR / 'anomaly_report.csv')))),
            ("Cancellation Rate", f"{float(k.get('Cancellation_Rate_Pct', 0)):.2f}%"),
        ]
        cols = st.columns(4)
        for i, (label, value) in enumerate(metrics):
            cols[i % 4].metric(label, value)
    else:
        st.info("No report yet. Upload a CSV or run the existing sample pipeline.")
        if st.button("Run Sample Data Analysis", type="primary"):
            try:
                from src.pipeline import run_pipeline
                run_pipeline()
                st.session_state["active_source"] = "Configured sample CSV files"
                st.rerun()
            except Exception as exc:
                st.error(f"Analysis failed: {exc}")
    monthly = read_csv_safe(REPORT_DIR / "monthly_sales.csv")
    if not monthly.empty and {"Month", "Revenue"}.issubset(monthly.columns):
        st.subheader("Monthly Revenue")
        st.bar_chart(monthly.set_index("Month")["Revenue"])
    branches = read_csv_safe(REPORT_DIR / "branch_analysis.csv")
    if not branches.empty:
        st.subheader("Branch Performance")
        st.dataframe(branches, use_container_width=True)

elif page == "Cleaned Data":
    st.subheader("Cleaned Data")
    df = read_csv_safe(PROCESSED_DIR / "cleaned_sales.csv")
    st.metric("Clean Records", len(df))
    if df.empty: st.info("No cleaned records yet.")
    else:
        st.dataframe(df, use_container_width=True, height=420)
        download_df("Download Cleaned CSV", df, "cleaned_sales.csv")

elif page == "Rejected Records":
    st.subheader("Rejected Records")
    df = read_csv_safe(PROCESSED_DIR / "rejected_records.csv")
    st.metric("Rejected Records", len(df))
    if df.empty: st.info("No rejected records in the latest run.")
    else: st.dataframe(df, use_container_width=True, height=420)
    download_df("Download Rejected CSV", df, "rejected_records.csv")

elif page == "Anomaly Detection":
    st.subheader("Anomaly Detection")
    df = read_csv_safe(PROCESSED_DIR / "anomaly_report.csv")
    st.metric("Anomaly Flags", len(df))
    if df.empty: st.info("No anomalies flagged in the latest run.")
    else: st.dataframe(df, use_container_width=True, height=420)
    download_df("Download Anomaly CSV", df, "anomaly_report.csv")

elif page == "Business Analytics":
    st.subheader("Business Analytics")
    files = [
        ("Branch Performance", "branch_analysis.csv", "Branch"),
        ("Product Performance", "product_analysis.csv", "Product_Name"),
        ("Category Performance", "category_analysis.csv", "Category"),
        ("Payment Analysis", "payment_analysis.csv", "Payment_Method"),
        ("Customer Analysis", "customer_analysis.csv", "Customer_Name"),
    ]
    for title, filename, index_col in files:
        data = read_csv_safe(REPORT_DIR / filename)
        with st.expander(title, expanded=(title == "Branch Performance")):
            if data.empty: st.info("No data available yet.")
            else:
                st.dataframe(data, use_container_width=True)
                if "Revenue" in data.columns and index_col in data.columns:
                    st.bar_chart(data[[index_col, "Revenue"]].dropna().head(20).set_index(index_col))

elif page == "Charts":
    st.subheader("Charts")
    chart_files = sorted(CHART_DIR.glob("*.png")) if CHART_DIR.exists() else []
    if not chart_files: st.info("No charts generated yet.")
    for start in range(0, len(chart_files), 2):
        cols = st.columns(2)
        for col, chart in zip(cols, chart_files[start:start+2]):
            with col:
                st.markdown(f"**{chart.stem.replace('_', ' ').title()}**")
                st.image(str(chart), use_container_width=True)

elif page == "Management Report":
    st.subheader("Management Report")
    report_path = REPORT_DIR / "management_report.txt"
    if report_path.exists():
        report_text = report_path.read_text(encoding="utf-8", errors="replace")
        st.text_area("Management report", report_text, height=350)
        st.download_button("Download Management Report", report_text.encode("utf-8"),
                           file_name="management_report.txt", mime="text/plain")
    else: st.info("Management report not generated yet.")

st.divider()
st.caption("Python • Pandas • SQLite • Streamlit | Local project dashboard")
