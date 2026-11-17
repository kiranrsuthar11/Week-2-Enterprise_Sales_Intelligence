import pandas as pd
import numpy as np
import re

def clean_sales_data(raw):
    df = raw.copy()
    for col in ["Transaction_ID", "Customer_ID", "Customer_Name", "Product_ID", "Product_Name", "Category", "Branch", "Payment_Method", "Order_Status"]:
        if col in df:
            df[col] = df[col].astype("string").str.replace(r"\s+", " ", regex=True).str.strip()
    for col in ["Quantity", "Unit_Price", "Discount"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    # Support 0.10 or 10 to mean a 10 percent discount.
    df.loc[df["Discount"] > 1, "Discount"] = df.loc[df["Discount"] > 1, "Discount"] / 100
    df["Transaction_Date"] = pd.to_datetime(df["Transaction_Date"], errors="coerce", format="mixed")
    duplicate = df["Transaction_ID"].duplicated(keep="first")
    invalid = (
        df["Transaction_ID"].isna() | df["Transaction_ID"].eq("") |
        df["Transaction_Date"].isna() | df["Quantity"].isna() | (df["Quantity"] <= 0) |
        df["Unit_Price"].isna() | (df["Unit_Price"] <= 0) |
        df["Discount"].isna() | (df["Discount"] < 0) | (df["Discount"] > 1)
    )
    rejected = df.loc[invalid | duplicate].copy()
    reasons = []
    for idx, row in rejected.iterrows():
        rs = []
        if pd.isna(row["Transaction_ID"]) or str(row["Transaction_ID"]).strip() == "": rs.append("Missing transaction ID")
        if pd.isna(row["Transaction_Date"]): rs.append("Invalid date")
        if pd.isna(row["Quantity"]) or row["Quantity"] <= 0: rs.append("Invalid quantity")
        if pd.isna(row["Unit_Price"]) or row["Unit_Price"] <= 0: rs.append("Invalid unit price")
        if pd.isna(row["Discount"]) or row["Discount"] < 0 or row["Discount"] > 1: rs.append("Invalid discount")
        if bool(duplicate.loc[idx]): rs.append("Duplicate transaction ID")
        reasons.append("; ".join(rs) or "Invalid record")
    rejected["Rejection_Reason"] = reasons
    df = df.loc[~(invalid | duplicate)].copy()
    # Fill optional descriptive fields so a valid transaction is not lost.
    for col, value in [("Customer_ID", "UNKNOWN"), ("Customer_Name", "Unknown Customer"), ("Product_Name", "Unknown Product"), ("Category", "Uncategorized"), ("Branch", "Unknown Branch"), ("Payment_Method", "Unknown"), ("Order_Status", "Unknown")]:
        df[col] = df[col].fillna(value).replace("", value)
    df["Product_Name"] = df["Product_Name"].str.title()
    df["Customer_Name"] = df["Customer_Name"].str.title()
    df["Category"] = df["Category"].str.title()
    df["Branch"] = df["Branch"].str.replace(r"\s+branch$", "", regex=True, case=False).str.strip().str.title()
    df["Payment_Method"] = df["Payment_Method"].str.replace("_", " ", regex=False).str.title()
    df["Payment_Method"] = df["Payment_Method"].replace({"Upi":"UPI", "Credit Card":"Credit Card", "Debit Card":"Debit Card", "Net Banking":"Net Banking"})
    df["Order_Status"] = df["Order_Status"].str.title().replace({"Canceled":"Cancelled"})
    df["Quantity"] = df["Quantity"].astype(int)
    df["Gross_Sales"] = df["Quantity"] * df["Unit_Price"]
    df["Discount_Amount"] = df["Gross_Sales"] * df["Discount"]
    df["Net_Sales"] = df["Gross_Sales"] - df["Discount_Amount"]
    dates = df["Transaction_Date"]
    df["Day_Name"] = dates.dt.day_name()
    df["Is_Weekend"] = dates.dt.dayofweek >= 5
    df["Day"] = dates.dt.strftime("%Y-%m-%d")
    df["Week"] = dates.dt.to_period("W").astype(str)
    df["Month"] = dates.dt.to_period("M").astype(str)
    df["Quarter"] = dates.dt.to_period("Q").astype(str)
    return df, rejected
