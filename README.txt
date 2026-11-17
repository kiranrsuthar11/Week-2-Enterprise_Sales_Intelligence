PROJECT TITLE
Enterprise Sales Data Processing, Analytics & Business Intelligence Automation System

FEATURES
- Automatically loads multiple CSV files from data/raw and combines them.
- Checks required columns, reports data-quality issues and shows data types.
- Cleans dates, text, numeric values, branch names and payment-method names.
- Saves duplicate/invalid transactions to rejected_records.csv with reasons.
- Calculates Gross_Sales, Discount_Amount and Net_Sales.
- Produces daily, weekly, monthly, quarterly, weekday/weekend and month-on-month analysis.
- Analyses products, categories, branches, customers, payment methods and discounts.
- Segments customers with simple rules (no machine learning).
- Flags unusual transactions for review.
- Stores transactions, customers, products, branches, rejected rows and anomalies in SQLite.
- Creates CSV outputs, charts, a data-quality report, management report and logs.
- Includes SQL examples, a Jupyter exploratory notebook, project architecture diagram and final presentation.

RUN IN WINDOWS / VS CODE
1. Extract this ZIP.
2. Open the extracted project folder in VS Code.
3. Open Terminal > New Terminal.
4. Create environment: python -m venv venv
5. Activate: .\venv\Scripts\activate
6. Install: pip install -r requirements.txt
7. Run: python main.py

REQUIRED CSV COLUMNS
Transaction_ID, Transaction_Date, Customer_ID, Customer_Name, Product_ID, Product_Name,
Category, Branch, Quantity, Unit_Price, Discount, Payment_Method, Order_Status

OUTPUTS
- data/processed/cleaned_sales.csv
- data/processed/rejected_records.csv
- data/processed/anomaly_report.csv
- data/processed/daily_sales.csv, weekly_sales.csv, monthly_sales.csv, quarterly_sales.csv
- reports/data_quality_report.csv, sales_kpis.csv, branch_analysis.csv, product_analysis.csv,
  category_analysis.csv, customer_analysis.csv, payment_analysis.csv, discount_analysis.csv
- reports/management_report.txt
- visualizations/*.png
- data/sales_database.db
- docs/project_architecture.png and docs/final_project_presentation.pptx
- logs/pipeline.log

NOTES
- Included sample data is synthetic for practice; figures are not real company results.
- Discount can be entered as 0.10 or 10 for 10 percent.
- Cancelled orders are included in operational/cancellation analysis; headline revenue uses completed/delivered orders when available.
- Confirm business-specific rules with your mentor before submitting. Optional Streamlit, MySQL, email reporting and scheduled execution are not enabled.

SIMPLE WEBSITE DASHBOARD
------------------------
A browser dashboard has been added in app.py.
To start it, install requirements and run:
    streamlit run app.py
Then open http://localhost:8501 if the browser does not open automatically.
See WEBSITE_START_HERE.txt for beginner-friendly steps.


WEBSITE CSV UPLOAD WORKFLOW (UPDATED)
=====================================
1. Run RUN_WEBSITE.bat and open http://localhost:8501.
2. Select "Upload Sales CSV" in the sidebar.
3. Choose one CSV file and click "Run Sales Analysis".
4. The uploaded dataset is passed directly to the pipeline. It is not combined
   with the sample CSVs in data/raw.
5. Review Dashboard, Cleaned Data, Rejected Records, Anomaly Detection,
   Business Analytics, Charts, and Management Report.
6. Use the download buttons on Cleaned Data, Rejected Records, Anomaly
   Detection, and Management Report to export the current generated outputs.

Required CSV columns:
Transaction_ID, Transaction_Date, Customer_ID, Customer_Name, Product_ID,
Product_Name, Category, Branch, Quantity, Unit_Price, Discount,
Payment_Method, Order_Status.

Invalid records are listed in data/processed/rejected_records.csv with
Rejection_Reason. Repeated transaction IDs are rejected after the first row.
Database transaction data is replaced by each successful run rather than
appended, preventing duplicate rows from repeated processing.

For uploaded data, the source file is stored separately in data/uploads.
Sample CSV files remain in data/raw and are used only when running the sample
pipeline (not when running an uploaded CSV).
