import sqlite3
from pathlib import Path

def save_database(df, database_path, rejected=None, anomalies=None):
    path = Path(database_path); path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        df.to_sql("transactions", conn, if_exists="replace", index=False)
        if rejected is not None: rejected.to_sql("rejected_records", conn, if_exists="replace", index=False)
        if anomalies is not None: anomalies.to_sql("anomalies", conn, if_exists="replace", index=False)
        df[["Customer_ID", "Customer_Name"]].drop_duplicates().to_sql("customers", conn, if_exists="replace", index=False)
        df[["Product_ID", "Product_Name", "Category"]].drop_duplicates().to_sql("products", conn, if_exists="replace", index=False)
        df[["Branch"]].drop_duplicates().to_sql("branches", conn, if_exists="replace", index=False)
        conn.execute("CREATE TABLE IF NOT EXISTS data_quality_logs (log_id INTEGER PRIMARY KEY, created_at TEXT DEFAULT CURRENT_TIMESTAMP, detail TEXT)")
        conn.execute("INSERT INTO data_quality_logs(detail) VALUES (?)", (f"Clean rows={len(df)}; rejected={len(rejected) if rejected is not None else 0}; anomalies={len(anomalies) if anomalies is not None else 0}",))
        conn.execute("CREATE INDEX IF NOT EXISTS idx_transactions_branch ON transactions (Branch)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_transactions_product ON transactions (Product_Name)")
