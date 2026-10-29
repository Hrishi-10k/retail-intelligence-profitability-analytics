USE retail_analytics;

-- 1. Check total transaction rows
SELECT COUNT(*) AS total_rows
FROM retail_transactions;

-- 2. Find the largest countries by transaction-line count
SELECT
    country,
    COUNT(*) AS transaction_lines
FROM retail_transactions
GROUP BY country
ORDER BY transaction_lines DESC
LIMIT 10;

-- 3. Investigate cancellations
SELECT
    is_cancellation,
    COUNT(*) AS transaction_lines,
    ROUND(SUM(line_value), 2) AS line_value_total
FROM retail_transactions
GROUP BY is_cancellation;