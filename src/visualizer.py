from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def create_charts(sales, monthly, output_dir):
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True); sns.set_theme(style="whitegrid")
    if not monthly.empty:
        fig, ax = plt.subplots(figsize=(9,5)); sns.lineplot(data=monthly, x="Month", y="Revenue", marker="o", ax=ax); ax.set_title("Monthly Revenue Trend"); ax.tick_params(axis="x", rotation=35); fig.tight_layout(); fig.savefig(out/"monthly_revenue.png", dpi=150); plt.close(fig)
    charts = [("Branch","branch_revenue.png","Branch-wise Revenue"),("Category","category_revenue.png","Category-wise Revenue"),("Payment_Method","payment_distribution.png","Payment Method Distribution")]
    for col, fn, title in charts:
        summary=sales.groupby(col,as_index=False)["Net_Sales"].sum().sort_values("Net_Sales",ascending=False)
        fig,ax=plt.subplots(figsize=(9,5)); sns.barplot(data=summary,x="Net_Sales",y=col,ax=ax,color="steelblue"); ax.set_title(title); fig.tight_layout(); fig.savefig(out/fn,dpi=150); plt.close(fig)
    top=sales.groupby("Product_Name",as_index=False)["Net_Sales"].sum().nlargest(10,"Net_Sales")
    fig,ax=plt.subplots(figsize=(9,5)); sns.barplot(data=top,y="Product_Name",x="Net_Sales",ax=ax,color="steelblue"); ax.set_title("Top 10 Products by Revenue"); fig.tight_layout(); fig.savefig(out/"top_products.png",dpi=150); plt.close(fig)
    segment_file=Path(__file__).resolve().parents[1]/"reports"/"customer_segments.csv"
    if segment_file.exists():
        seg=pd.read_csv(segment_file)
        if not seg.empty:
            fig,ax=plt.subplots(figsize=(8,5)); sns.barplot(data=seg,x="Customer_Segment",y="Customer_Count",ax=ax,color="steelblue"); ax.set_title("Customer Segment Distribution"); ax.tick_params(axis="x",rotation=25); fig.tight_layout(); fig.savefig(out/"customer_segment_distribution.png",dpi=150); plt.close(fig)
    discount_file=Path(__file__).resolve().parents[1]/"reports"/"discount_analysis.csv"
    if discount_file.exists():
        dis=pd.read_csv(discount_file)
        if not dis.empty:
            fig,ax=plt.subplots(figsize=(8,5)); sns.barplot(data=dis,x="Discount_Band",y="Revenue",ax=ax,color="steelblue"); ax.set_title("Discount Band vs Revenue"); fig.tight_layout(); fig.savefig(out/"discount_vs_sales.png",dpi=150); plt.close(fig)
    branch_file=Path(__file__).resolve().parents[1]/"reports"/"branch_analysis.csv"
    if branch_file.exists():
        br=pd.read_csv(branch_file)
        if "Cancellation_Rate_Pct" in br and not br.empty:
            fig,ax=plt.subplots(figsize=(8,5)); sns.barplot(data=br,x="Cancellation_Rate_Pct",y="Branch",ax=ax,color="steelblue"); ax.set_title("Cancellation Rate by Branch"); fig.tight_layout(); fig.savefig(out/"cancellation_rate_by_branch.png",dpi=150); plt.close(fig)
