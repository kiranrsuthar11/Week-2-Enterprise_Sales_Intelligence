import pandas as pd
import numpy as np
from pathlib import Path

def create_summaries(df, output_dir):
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    data = df.copy()
    cancelled_mask = data["Order_Status"].str.lower().eq("cancelled")
    completed = data[data["Order_Status"].str.lower().isin(["completed", "complete", "delivered", "success"])].copy()
    sales = completed if not completed.empty else data.copy()
    total_revenue = float(sales["Net_Sales"].sum())
    total_orders = int(data["Transaction_ID"].nunique())
    completed_orders = int(completed["Transaction_ID"].nunique())
    cancelled_orders = int(data.loc[cancelled_mask, "Transaction_ID"].nunique())
    kpis = pd.DataFrame([{
        "Total_Revenue": round(total_revenue, 2), "Total_Orders": total_orders,
        "Average_Order_Value": round(total_revenue / max(completed_orders, 1), 2),
        "Units_Sold": int(sales["Quantity"].sum()), "Total_Discount": round(float(sales["Discount_Amount"].sum()), 2),
        "Cancelled_Orders": cancelled_orders, "Completed_Orders": completed_orders,
        "Cancellation_Rate_Pct": round(100 * cancelled_mask.sum() / max(len(data), 1), 2),
        "Total_Customers": int(data["Customer_ID"].nunique()),
        "Repeat_Customers": int((data.groupby("Customer_ID")["Transaction_ID"].nunique() > 1).sum())
    }])
    kpis.to_csv(out / "sales_kpis.csv", index=False)

    product_all = data.groupby(["Product_ID", "Product_Name"], as_index=False).agg(Revenue=("Net_Sales", "sum"), Quantity_Sold=("Quantity", "sum"), Orders=("Transaction_ID", "nunique"), Average_Discount=("Discount", "mean"))
    product_all["Cancellation_Rate_Pct"] = data.groupby(["Product_ID", "Product_Name"])["Order_Status"].apply(lambda s: 100*s.str.lower().eq("cancelled").mean()).values
    product_all["Performance_Flag"] = np.where((product_all["Revenue"] <= product_all["Revenue"].quantile(.25)) & (product_all["Quantity_Sold"] <= product_all["Quantity_Sold"].quantile(.25)), "Low Performing", "Normal")
    product_all.sort_values("Revenue", ascending=False).to_csv(out / "product_analysis.csv", index=False)
    product_all.nlargest(10, "Revenue").to_csv(out / "top_10_products.csv", index=False)
    product_all.nsmallest(10, "Revenue").to_csv(out / "low_performing_products.csv", index=False)

    branch = data.groupby("Branch", as_index=False).agg(Revenue=("Net_Sales", "sum"), Orders=("Transaction_ID", "nunique"), Quantity_Sold=("Quantity", "sum"), Discount=("Discount_Amount", "sum"))
    cancel_rates = data.assign(Is_Cancelled=cancelled_mask).groupby("Branch")["Is_Cancelled"].mean()*100
    branch["Cancellation_Rate_Pct"] = branch["Branch"].map(cancel_rates)
    branch["Average_Order_Value"] = branch["Revenue"] / branch["Orders"].replace(0, np.nan)
    branch.sort_values("Revenue", ascending=False).to_csv(out / "branch_analysis.csv", index=False)

    category = data.groupby("Category", as_index=False).agg(Revenue=("Net_Sales", "sum"), Quantity_Sold=("Quantity", "sum"), Orders=("Transaction_ID", "nunique"), Average_Discount=("Discount", "mean"))
    category.sort_values("Revenue", ascending=False).to_csv(out / "category_analysis.csv", index=False)

    payment = data.groupby("Payment_Method", as_index=False).agg(Transactions=("Transaction_ID", "nunique"), Revenue=("Net_Sales", "sum"))
    payment["Average_Transaction_Value"] = payment["Revenue"] / payment["Transactions"].replace(0, np.nan)
    payment["Revenue_Contribution_Pct"] = payment["Revenue"] / max(payment["Revenue"].sum(), 1)*100
    payment.sort_values("Transactions", ascending=False).to_csv(out / "payment_analysis.csv", index=False)

    customer = data.groupby(["Customer_ID", "Customer_Name"], as_index=False).agg(Orders=("Transaction_ID", "nunique"), Revenue=("Net_Sales", "sum"), Total_Discount=("Discount_Amount", "sum"), Average_Discount=("Discount", "mean"))
    customer["Customer_Segment"] = np.select([customer["Orders"].eq(1), customer["Revenue"].ge(50000), customer["Revenue"].ge(20000)], ["One-Time Customer", "High Value Customer", "Regular Customer"], default="Low Value Customer")
    customer.to_csv(out / "customer_analysis.csv", index=False)
    customer["Customer_Segment"].value_counts().rename_axis("Customer_Segment").reset_index(name="Customer_Count").to_csv(out / "customer_segments.csv", index=False)
    customer.sort_values("Total_Discount", ascending=False).head(10).to_csv(out / "top_discount_customers.csv", index=False)

    for period, fname in [("Day", "daily_sales.csv"), ("Week", "weekly_sales.csv"), ("Month", "monthly_sales.csv"), ("Quarter", "quarterly_sales.csv")]:
        frame = sales.groupby(period, as_index=False).agg(Revenue=("Net_Sales", "sum"), Orders=("Transaction_ID", "nunique"), Units_Sold=("Quantity", "sum"))
        if period == "Month":
            frame["MoM_Growth_Pct"] = frame["Revenue"].pct_change()*100
        frame.to_csv(out / fname, index=False)
    monthly = pd.read_csv(out / "monthly_sales.csv"); monthly = monthly.rename(columns={"Month":"Month"})
    weekday = sales.groupby("Is_Weekend", as_index=False).agg(Revenue=("Net_Sales", "sum"), Orders=("Transaction_ID", "nunique"))
    weekday["Day_Type"] = weekday["Is_Weekend"].map({True:"Weekend", False:"Weekday"})
    weekday.to_csv(out / "weekend_vs_weekday.csv", index=False)

    data.assign(Discount_Band=pd.cut(data["Discount"], [-.001,0,.1,.25,.5,1], labels=["0%","0-10%","10-25%","25-50%","50%+"])).groupby("Discount_Band", observed=False, as_index=False).agg(Transactions=("Transaction_ID","nunique"), Revenue=("Net_Sales","sum"), Average_Discount=("Discount","mean")).to_csv(out / "discount_analysis.csv", index=False)
    data[data["Discount"] > .5].to_csv(out / "high_discount_transactions.csv", index=False)
    data["Transaction_Date"] = pd.to_datetime(data["Transaction_Date"])
    monthly = sales.assign(Month=sales["Transaction_Date"].dt.to_period("M").astype(str)).groupby("Month", as_index=False)["Net_Sales"].sum().rename(columns={"Net_Sales":"Revenue"})
    monthly.to_csv(out / "monthly_sales.csv", index=False)
    return kpis, sales, monthly
