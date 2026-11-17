-- Total revenue from completed/delivered orders
SELECT SUM(Net_Sales) AS total_revenue FROM transactions
WHERE lower(Order_Status) IN ('completed','complete','delivered','success');

-- Monthly sales
SELECT Month, SUM(Net_Sales) AS revenue FROM transactions GROUP BY Month ORDER BY Month;

-- Branch performance
SELECT Branch, SUM(Net_Sales) AS total_sales, COUNT(DISTINCT Transaction_ID) AS total_orders
FROM transactions GROUP BY Branch ORDER BY total_sales DESC;

-- Product performance
SELECT Product_Name, SUM(Net_Sales) AS revenue, SUM(Quantity) AS units_sold
FROM transactions GROUP BY Product_Name ORDER BY revenue DESC;

-- Top customer spending
SELECT Customer_ID, Customer_Name, SUM(Net_Sales) AS spending
FROM transactions GROUP BY Customer_ID, Customer_Name ORDER BY spending DESC LIMIT 20;

-- Duplicate IDs (normally duplicates are retained in rejected_records, not transactions)
SELECT Transaction_ID, COUNT(*) AS occurrences FROM transactions GROUP BY Transaction_ID HAVING COUNT(*) > 1;

-- Cancelled orders
SELECT * FROM transactions WHERE lower(Order_Status)='cancelled';

-- High value transactions
SELECT * FROM transactions WHERE Net_Sales > 100000 ORDER BY Net_Sales DESC;
