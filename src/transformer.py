"""Reusable sales transformations."""
import pandas as pd

def add_sales_metrics(df):
    result = df.copy()
    result["Gross_Sales"] = result["Quantity"] * result["Unit_Price"]
    result["Discount_Amount"] = result["Gross_Sales"] * result["Discount"]
    result["Net_Sales"] = result["Gross_Sales"] - result["Discount_Amount"]
    return result

def add_time_features(df, date_column="Transaction_Date"):
    result = df.copy()
    result[date_column] = pd.to_datetime(result[date_column], errors="coerce", format="mixed")
    result["Day"] = result[date_column].dt.strftime("%Y-%m-%d")
    result["Week"] = result[date_column].dt.to_period("W").astype(str)
    result["Month"] = result[date_column].dt.to_period("M").astype(str)
    result["Quarter"] = result[date_column].dt.to_period("Q").astype(str)
    return result
