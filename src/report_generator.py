from pathlib import Path
import pandas as pd

def generate_management_report(kpis, branch_csv, product_csv, category_csv, payment_csv, output_file, rejected_count=0, anomaly_count=0):
    out=Path(output_file); out.parent.mkdir(parents=True,exist_ok=True); row=kpis.iloc[0]
    def first(path,col):
        df=pd.read_csv(path); return str(df.iloc[0][col]) if not df.empty else "Not available"
    branches=pd.read_csv(branch_csv); products=pd.read_csv(product_csv); categories=pd.read_csv(category_csv); payments=pd.read_csv(payment_csv)
    lines=["ENTERPRISE SALES DATA PROCESSING, ANALYTICS & BUSINESS INTELLIGENCE AUTOMATION SYSTEM","="*82,"","EXECUTIVE SUMMARY",
      f"Total Revenue: ₹{row['Total_Revenue']:,.2f}",f"Total Orders: {int(row['Total_Orders'])}",f"Completed Orders: {int(row['Completed_Orders'])}",f"Cancelled Orders: {int(row['Cancelled_Orders'])}",f"Cancellation Rate: {row['Cancellation_Rate_Pct']:.2f}%",f"Average Order Value: ₹{row['Average_Order_Value']:,.2f}",f"Units Sold: {int(row['Units_Sold'])}",f"Total Discount: ₹{row['Total_Discount']:,.2f}",f"Unique Customers: {int(row['Total_Customers'])}",f"Repeat Customers: {int(row['Repeat_Customers'])}",f"Rejected Records: {rejected_count}",f"Flagged Anomalies: {anomaly_count}","","TOP PERFORMERS",
      f"Top Branch: {first(branch_csv,'Branch')}",f"Top Product: {first(product_csv,'Product_Name')}",f"Top Category: {first(category_csv,'Category')}",f"Most Used Payment Method: {first(payment_csv,'Payment_Method')}","","KEY FINDINGS & RECOMMENDATIONS"]
    if not branches.empty:
        b=branches.sort_values("Cancellation_Rate_Pct",ascending=False).iloc[0]
        lines.append(f"- Review cancellation reasons at {b['Branch']} (rate {b['Cancellation_Rate_Pct']:.1f}%).")
    if anomaly_count: lines.append(f"- Review {anomaly_count} flagged transactions; anomaly flags are not proof of fraud.")
    if not products.empty and (products.get("Performance_Flag",pd.Series(dtype=str))=="Low Performing").any(): lines.append("- Review low-performing products before offering additional discounts.")
    lines += ["- Encourage repeat purchases from one-time customers through retention offers.","- Compare discount bands with revenue and order volume before changing pricing.","- Validate these findings against official business data before operational decisions.","","OUTPUTS","See data/processed, reports, visualizations, logs and data/sales_database.db."]
    out.write_text("\n".join(lines),encoding="utf-8")
