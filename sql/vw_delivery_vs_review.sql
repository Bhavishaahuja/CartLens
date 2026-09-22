CREATE OR REPLACE VIEW `cartlens.vw_delivery_vs_review` AS

-- One review score per order (a few orders have multiple review rows).
WITH order_review AS (
  SELECT
    order_id,
    AVG(review_score) AS review_score
  FROM `cartlens.order_reviews`
  GROUP BY order_id
),

-- Delivered orders only, with the delivery math worked out.
delivered AS (
  SELECT
    o.order_id,
    DATE_DIFF(DATE(o.order_delivered_customer_date), DATE(o.order_purchase_timestamp), DAY) AS actual_delivery_days,
    DATE_DIFF(DATE(o.order_estimated_delivery_date), DATE(o.order_purchase_timestamp), DAY) AS estimated_delivery_days,
    DATE_DIFF(DATE(o.order_delivered_customer_date), DATE(o.order_estimated_delivery_date), DAY) AS days_vs_estimate
  FROM `cartlens.orders` o
  WHERE o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL
    AND o.order_estimated_delivery_date IS NOT NULL
)

SELECT
  d.order_id,
  d.actual_delivery_days,        -- how many days it really took
  d.estimated_delivery_days,     -- how many days were promised
  d.days_vs_estimate,            -- + = late, - = early
  CASE
    WHEN d.days_vs_estimate > 0 THEN 'Late'
    WHEN d.days_vs_estimate = 0 THEN 'On Time'
    ELSE 'Early'
  END AS delivery_status,
  r.review_score
FROM delivered d
LEFT JOIN order_review r
  ON d.order_id = r.order_id;