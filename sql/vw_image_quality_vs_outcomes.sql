CREATE OR REPLACE VIEW `cartlens.vw_image_quality_vs_outcomes` AS

-- Average image-quality signals per category. Only the 3 mapped categories
-- (electronics, fashion_male_clothing, furniture_decor) have images.
WITH image_stats AS (
  SELECT
    olist_category AS category,
    COUNT(*)                            AS images_sampled,
    ROUND(AVG(blur_score), 1)           AS avg_sharpness,    -- higher = sharper
    ROUND(AVG(brightness), 1)           AS avg_brightness,
    ROUND(AVG(width_px * height_px), 0) AS avg_pixels
  FROM `cartlens.product_image_features`
  GROUP BY olist_category
),

-- Sales outcomes per category.
sales AS (
  SELECT
    p.product_category_name_english AS category,
    COUNT(*)                AS items_sold,
    ROUND(SUM(oi.price), 2) AS revenue,
    ROUND(AVG(oi.price), 2) AS avg_item_price
  FROM `cartlens.order_items` oi
  JOIN `cartlens.products` p
    ON oi.product_id = p.product_id
  GROUP BY p.product_category_name_english
),

-- Review outcomes per category (each order's review attributed to the
-- categories of the items in that order).
reviews AS (
  SELECT
    p.product_category_name_english AS category,
    ROUND(AVG(r.review_score), 3) AS avg_review
  FROM `cartlens.order_reviews` r
  JOIN `cartlens.order_items` oi
    ON r.order_id = oi.order_id
  JOIN `cartlens.products` p
    ON oi.product_id = p.product_id
  GROUP BY p.product_category_name_english
)

-- Line up image quality next to real business outcomes, per category.
SELECT
  i.category,
  i.images_sampled,
  i.avg_sharpness,
  i.avg_brightness,
  i.avg_pixels,
  s.items_sold,
  s.revenue,
  s.avg_item_price,
  rv.avg_review
FROM image_stats i
JOIN sales s    ON i.category = s.category
JOIN reviews rv ON i.category = rv.category
ORDER BY i.avg_sharpness DESC;