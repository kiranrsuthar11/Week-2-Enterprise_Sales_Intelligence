import pandas as pd

def build_quality_report(df):
    quantity = pd.to_numeric(df["Quantity"], errors="coerce")
    price = pd.to_numeric(df["Unit_Price"], errors="coerce")
    discount = pd.to_numeric(df["Discount"], errors="coerce")
    dates = pd.to_datetime(df["Transaction_Date"], errors="coerce", format="mixed")
    report = {
        "Total_Records": len(df),
        "Missing_Values_Total": int(df.isna().sum().sum()),
        "Missing_Customer_Name": int(df["Customer_Name"].isna().sum() + df["Customer_Name"].astype(str).str.strip().eq("").sum()),
        "Missing_Product_Name": int(df["Product_Name"].isna().sum() + df["Product_Name"].astype(str).str.strip().eq("").sum()),
        "Missing_Unit_Price": int(price.isna().sum()),
        "Duplicate_Transaction_ID_Rows": int(df["Transaction_ID"].duplicated(keep=False).sum()),
        "Invalid_Quantity_Rows": int((quantity.isna() | (quantity <= 0)).sum()),
        "Invalid_Price_Rows": int((price.isna() | (price <= 0)).sum()),
        "Invalid_Date_Rows": int(dates.isna().sum()),
        "Invalid_Discount_Rows": int((discount.isna() | (discount < 0) | (discount > 100)).sum()),
    }
    return pd.DataFrame([{"Check": k, "Count": int(v)} for k, v in report.items()])
