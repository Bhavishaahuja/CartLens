-- Day 1 checkpoint: confirm the image features join cleanly to real products
SELECT
  f.olist_category,
  COUNT(DISTINCT f.image_file)   AS images,
  ROUND(AVG(f.brightness), 1)    AS avg_brightness,
  ROUND(AVG(f.blur_score), 1)    AS avg_sharpness,
  COUNT(DISTINCT p.product_id)   AS products_in_category
FROM `cartlens-509400.cartlens.product_image_features` AS f
LEFT JOIN `cartlens-509400.cartlens.products` AS p
  ON f.olist_category = p.product_category_name_english
GROUP BY f.olist_category
ORDER BY f.olist_category;