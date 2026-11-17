"""Branch performance and cancellation metrics."""

def analyze_branches(df):
    result = df.groupby("Branch", as_index=False).agg(
        Revenue=("Net_Sales", "sum"), Orders=("Transaction_ID", "nunique"),
        Units_Sold=("Quantity", "sum"), Discount_Amount=("Discount_Amount", "sum"))
    cancelled = df.assign(_cancelled=df["Order_Status"].str.lower().eq("cancelled")).groupby("Branch")["_cancelled"].mean()*100
    result["Cancellation_Rate_Pct"] = result["Branch"].map(cancelled)
    return result.sort_values("Revenue", ascending=False)
