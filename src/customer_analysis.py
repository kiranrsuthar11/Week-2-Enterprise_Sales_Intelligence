"""Customer summaries and simple rule-based segments."""
import pandas as pd

def analyze_customers(df, high_value=50000, regular_value=20000):
    customers = df.groupby(["Customer_ID", "Customer_Name"], as_index=False).agg(
        Orders=("Transaction_ID", "nunique"), Revenue=("Net_Sales", "sum"),
        Total_Discount=("Discount_Amount", "sum"))
    customers["Customer_Segment"] = customers["Revenue"].apply(
        lambda x: "High Value Customer" if x >= high_value else ("Regular Customer" if x >= regular_value else "Low Value Customer"))
    customers.loc[customers["Orders"] == 1, "Customer_Segment"] = "One-Time Customer"
    return customers
