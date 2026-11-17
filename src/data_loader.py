from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = [
    "Transaction_ID", "Transaction_Date", "Customer_ID", "Customer_Name",
    "Product_ID", "Product_Name", "Category", "Branch", "Quantity",
    "Unit_Price", "Discount", "Payment_Method", "Order_Status"
]

def load_sales_files(input_dir):
    folder = Path(input_dir)
    csv_files = sorted(folder.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in {folder}. Add sales CSV files and run again."
        )
    frames = []
    for file in csv_files:
        frame = pd.read_csv(file)
        frame.columns = [str(c).strip() for c in frame.columns]
        missing = [c for c in REQUIRED_COLUMNS if c not in frame.columns]
        if missing:
            raise ValueError(f"{file.name} is missing required columns: {missing}")
        frame["Source_File"] = file.name
        frames.append(frame)
        print(f"Loaded {file.name}: {len(frame)} records")
    combined = pd.concat(frames, ignore_index=True)
    print(f"Combined dataset: {len(combined)} records")
    print("\nData types:")
    print(combined.dtypes)
    return combined
