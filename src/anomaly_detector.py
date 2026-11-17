import pandas as pd

def detect_anomalies(df):
    flagged = []
    for _, row in df.iterrows():
        reasons = []
        if row.get("Quantity", 0) > 100: reasons.append("Quantity exceeds 100")
        if row.get("Discount", 0) > 0.50: reasons.append("Discount exceeds 50%")
        if row.get("Net_Sales", 0) > 100000: reasons.append("High transaction value")
        if row.get("Quantity", 0) < 0: reasons.append("Negative quantity")
        if row.get("Unit_Price", 0) < 0: reasons.append("Negative price")
        if reasons:
            item = row.to_dict(); item["Anomaly_Reasons"] = "; ".join(reasons); item["Review_Status"] = "REVIEW REQUIRED"; flagged.append(item)
    return pd.DataFrame(flagged, columns=list(df.columns)+["Anomaly_Reasons","Review_Status"])
