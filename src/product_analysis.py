"""Product and category performance summaries."""

def analyze_products(df):
    return df.groupby(["Product_ID", "Product_Name", "Category"], as_index=False).agg(
        Revenue=("Net_Sales", "sum"), Units_Sold=("Quantity", "sum"),
        Orders=("Transaction_ID", "nunique"), Average_Discount=("Discount", "mean"))
