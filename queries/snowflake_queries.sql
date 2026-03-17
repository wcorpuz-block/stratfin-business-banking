-- ============================================================
-- Block Business Banking - Snowflake Queries
-- ============================================================

-- Instant Transfer: average transaction value and frequency
SELECT
    AVG(transaction_amount)                        AS avg_transaction_value,
    COUNT(*) / COUNT(DISTINCT customer_id)         AS monthly_transactions_per_customer
FROM transactions
WHERE product = 'instant_transfer'
  AND month = DATE_TRUNC('month', CURRENT_DATE);


-- Credit Card: average monthly spend per customer
SELECT
    customer_id,
    SUM(transaction_amount)                        AS monthly_spend
FROM transactions
WHERE product = 'credit_card'
  AND month = DATE_TRUNC('month', CURRENT_DATE)
GROUP BY customer_id;


-- Debit Card: average monthly spend per customer
SELECT
    customer_id,
    SUM(transaction_amount)                        AS monthly_spend
FROM transactions
WHERE product = 'debit_card'
  AND month = DATE_TRUNC('month', CURRENT_DATE)
GROUP BY customer_id;
