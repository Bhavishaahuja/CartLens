CREATE OR REPLACE VIEW `cartlens.vw_category_affinity` AS

-- The distinct set of categories in each order.
WITH order_categories AS (
  SELECT DISTINCT
    oi.order_id,
    COALESCE(p.product_category_name_english, 'unknown') AS category
  FROM `cartlens.order_items` oi
  JOIN `cartlens.products` p
    ON oi.product_id = p.product_id
),

-- Join the category list to itself on the same order to form pairs.
-- a.category < b.category keeps each pair once and drops self-pairs.
category_pairs AS (
  SELECT
    a.order_id,
    a.category AS cat_a,
    b.category AS cat_b
  FROM order_categories a
  JOIN order_categories b
    ON a.order_id = b.order_id
   AND a.category < b.category
  WHERE a.category <> 'unknown'
    AND b.category <> 'unknown'
)

-- Count how many orders each category pair appears in together.
SELECT
  cat_a,
  cat_b,
  COUNT(DISTINCT order_id) AS orders_together
FROM category_pairs
GROUP BY cat_a, cat_b
ORDER BY orders_together DESC;