CREATE OR REPLACE VIEW `cartlens.vw_rfm_segments` AS

-- Roll payments up to one total per order first, so we don't double-count
-- when an order was paid in multiple installments/rows.
WITH order_pay AS (
  SELECT
    order_id,
    SUM(payment_value) AS order_value
  FROM `cartlens.order_payments`
  GROUP BY order_id
),

-- One row per order, tagged with the REAL customer (customer_unique_id)
-- and what that order was worth.
order_level AS (
  SELECT
    c.customer_unique_id,
    o.order_id,
    o.order_purchase_timestamp,
    COALESCE(op.order_value, 0) AS order_value
  FROM `cartlens.orders` o
  JOIN `cartlens.customers` c
    ON o.customer_id = c.customer_id
  LEFT JOIN order_pay op
    ON o.order_id = op.order_id
),

-- Pick our "today": the last purchase anywhere in the dataset.
reference AS (
  SELECT MAX(order_purchase_timestamp) AS as_of_date
  FROM order_level
),

-- Collapse orders down to one row per customer with raw R, F, M.
customer_rfm AS (
  SELECT
    ol.customer_unique_id,
    DATE_DIFF(DATE(r.as_of_date), DATE(MAX(ol.order_purchase_timestamp)), DAY) AS recency_days,
    COUNT(DISTINCT ol.order_id) AS frequency,
    SUM(ol.order_value)         AS monetary
  FROM order_level ol
  CROSS JOIN reference r
  GROUP BY ol.customer_unique_id
),

-- Turn raw R and M into 1-5 quintile scores. (We deliberately do NOT
-- NTILE frequency, because 97% of customers share the value 1.)
scored AS (
  SELECT
    *,
    NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,  -- fewest days ago -> score 5
    NTILE(5) OVER (ORDER BY monetary ASC)      AS m_score   -- biggest spender -> score 5
  FROM customer_rfm
)

-- Label each customer. Order matters: CASE stops at the first match.
SELECT
  customer_unique_id,
  recency_days,
  frequency,
  monetary,
  r_score,
  m_score,
  CASE
    WHEN frequency >= 2 AND r_score >= 4 THEN 'Champions'          -- came back AND recently
    WHEN frequency >= 2 AND r_score >= 3 THEN 'Loyal'              -- came back, still fairly active
    WHEN frequency >= 2 AND r_score <= 2 THEN 'At Risk'            -- used to repeat, gone quiet
    WHEN frequency = 1 AND r_score >= 4 AND m_score >= 4 THEN 'Recent High-Value'  -- one big recent order
    WHEN frequency = 1 AND r_score >= 4 THEN 'New / Promising'     -- just arrived, single order
    WHEN r_score <= 2 THEN 'Hibernating'                          -- long time, no return
    ELSE 'Needs Attention'
  END AS segment
FROM scored;