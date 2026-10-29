-- Monthly sales trends
SELECT
    DATE_FORMAT(invoicedate, '%Y-%m') AS sales_month,
    ROUND(SUM(line_value), 2) AS preliminary_line_value,
    COUNT(DISTINCT invoiceno) AS invoice_count
FROM retail_transactions
WHERE is_cancellation = 0
  AND quantity > 0
  AND unitprice > 0
GROUP BY DATE_FORMAT(invoicedate, '%Y-%m')
ORDER BY sales_month;

-- Top 10 Products by preliminary sales values
SELECT
    stockcode,
    MAX(description) AS product_description,
    ROUND(SUM(line_value), 2) AS preliminary_sales_value,
    SUM(quantity) AS units_sold
FROM retail_transactions
WHERE is_cancellation = 0
  AND quantity > 0
  AND unitprice > 0
GROUP BY stockcode
ORDER BY preliminary_sales_value DESC
LIMIT 10;