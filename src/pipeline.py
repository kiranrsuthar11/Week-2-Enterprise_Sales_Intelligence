from pathlib import Path
import logging
import pandas as pd
import json
from .data_loader import load_sales_files
from .validator import build_quality_report
from .cleaner import clean_sales_data
from .anomaly_detector import detect_anomalies
from .sales_analysis import create_summaries
from .database import save_database
from .report_generator import generate_management_report
from .visualizer import create_charts

ROOT = Path(__file__).resolve().parents[1]

def run_pipeline(input_df=None, source_name=None):
    config_path = ROOT / "config" / "config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    path_keys = ["input_dir", "processed_dir", "reports_dir", "visualizations_dir", "database_path", "log_path"]
    paths = {key: (ROOT / config[key]).resolve() for key in path_keys}
    paths["log_path"].parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=paths["log_path"], level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s", force=True)
    try:
        for key in ["processed_dir", "reports_dir", "visualizations_dir"]:
            paths[key].mkdir(parents=True, exist_ok=True)
        if input_df is not None:
            raw = input_df.copy()
            raw.columns = [str(c).strip() for c in raw.columns]
            from .data_loader import REQUIRED_COLUMNS
            missing = [c for c in REQUIRED_COLUMNS if c not in raw.columns]
            if missing:
                raise ValueError(f"Uploaded CSV is missing required columns: {missing}")
            raw["Source_File"] = source_name or "uploaded.csv"
            logging.info("Processing uploaded dataset %s with %s records", source_name or "uploaded.csv", len(raw))
        else:
            raw = load_sales_files(paths["input_dir"])
        processed, reports, charts = paths["processed_dir"], paths["reports_dir"], paths["visualizations_dir"]
        quality = build_quality_report(raw)
        quality.to_csv(reports / "data_quality_report.csv", index=False)
        quality.to_csv(processed / "data_quality_report.csv", index=False)
        cleaned, rejected = clean_sales_data(raw)
        cleaned.to_csv(processed / "cleaned_sales.csv", index=False)
        rejected.to_csv(processed / "rejected_records.csv", index=False)
        anomalies = detect_anomalies(cleaned)
        anomalies.to_csv(processed / "anomaly_report.csv", index=False)
        kpis, sales, monthly = create_summaries(cleaned, reports)
        save_database(cleaned, paths["database_path"], rejected, anomalies)
        create_charts(sales, monthly, charts)
        generate_management_report(kpis, reports/"branch_analysis.csv", reports/"product_analysis.csv",
            reports/"category_analysis.csv", reports/"payment_analysis.csv", reports/"management_report.txt",
            len(rejected), len(anomalies))
        # Export standard SQL query outputs for review.
        import sqlite3
        sql_queries = {
            "sql_total_revenue.csv": "SELECT SUM(Net_Sales) AS total_revenue FROM transactions WHERE lower(Order_Status) IN ('completed','complete','delivered','success')",
            "sql_monthly_sales.csv": "SELECT Month, SUM(Net_Sales) AS revenue FROM transactions GROUP BY Month ORDER BY Month",
            "sql_branch_performance.csv": "SELECT Branch, SUM(Net_Sales) AS revenue, COUNT(DISTINCT Transaction_ID) AS orders FROM transactions GROUP BY Branch ORDER BY revenue DESC",
            "sql_top_customers.csv": "SELECT Customer_ID, Customer_Name, SUM(Net_Sales) AS spending FROM transactions GROUP BY Customer_ID, Customer_Name ORDER BY spending DESC LIMIT 20",
            "sql_cancelled_orders.csv": "SELECT * FROM transactions WHERE lower(Order_Status)='cancelled'",
            "sql_high_value_transactions.csv": "SELECT * FROM transactions WHERE Net_Sales > 100000 ORDER BY Net_Sales DESC"
        }
        with sqlite3.connect(paths["database_path"]) as conn:
            for filename, query in sql_queries.items():
                pd.read_sql_query(query, conn).to_csv(processed/filename, index=False)
        logging.info("Pipeline completed: raw=%s clean=%s rejected=%s anomalies=%s", len(raw), len(cleaned), len(rejected), len(anomalies))
        print("\nPROJECT COMPLETED SUCCESSFULLY")
        print(f"Raw records: {len(raw)}")
        print(f"Clean records: {len(cleaned)}")
        print(f"Rejected records: {len(rejected)}")
        print(f"Anomaly flags: {len(anomalies)}")
        print(f"Management report: {reports / 'management_report.txt'}")
        print(f"Charts folder: {charts}")
    except Exception as exc:
        logging.exception("Pipeline failed")
        print(f"ERROR: {exc}")
        print(f"Check {paths['log_path']} and confirm your configured input folder contains valid CSV files.")
        raise
