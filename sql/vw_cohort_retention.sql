CREATE OR REPLACE VIEW `cartlens.vw_cohort_retention` AS

-- Step 1: each customer's FIRST purchase month = their cohort.
WITH first_purchase AS (
  SELECT
    c.customer_unique_id,
    DATE_TRUNC(DATE(MIN(o.order_purchase_timestamp)), MONTH) AS cohort_month
  FROM `cartlens.orders` o
  JOIN `cartlens.customers` c
    ON o.customer_id = c.customer_id
  GROUP BY c.customer_unique_id
),

-- Step 2: every order, tagged with its cohort and how many months
-- after the first purchase it landed (0 = the first month itself).
orders_tagged AS (
  SELECT
    fp.cohort_month,
    fp.customer_unique_id,
    DATE_DIFF(
      DATE_TRUNC(DATE(o.order_purchase_timestamp), MONTH),
      fp.cohort_month,
      MONTH
    ) AS month_number
  FROM `cartlens.orders` o
  JOIN `cartlens.customers` c
    ON o.customer_id = c.customer_id
  JOIN first_purchase fp
    ON c.customer_unique_id = fp.customer_unique_id
),

-- Step 3: how many distinct customers from each cohort were active
-- in each month offset.
cohort_counts AS (
  SELECT
    cohort_month,
    month_number,
    COUNT(DISTINCT customer_unique_id) AS active_customers
  FROM orders_tagged
  GROUP BY cohort_month, month_number
),

-- Step 4: cohort size = the month-0 count (everyone in the cohort).
cohort_size AS (
  SELECT
    cohort_month,
    active_customers AS cohort_customers
  FROM cohort_counts
  WHERE month_number = 0
)

-- Final: retention percent per cohort per month.
SELECT
  cc.cohort_month,
  cc.month_number,
  cs.cohort_customers,
  cc.active_customers,
  ROUND(cc.active_customers / cs.cohort_customers * 100, 2) AS retention_pct
FROM cohort_counts cc
JOIN cohort_size cs
  ON cc.cohort_month = cs.cohort_month
ORDER BY cc.cohort_month, cc.month_number;