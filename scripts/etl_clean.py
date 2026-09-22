import os
import pandas as pd

raw_folder = "data"
clean_folder = os.path.join("data", "clean")

# make the output folder if it doesn't exist yet
os.makedirs(clean_folder, exist_ok=True)


# tiny helper to read a raw olist csv by filename
def load_raw(name):
    return pd.read_csv(os.path.join(raw_folder, name))


# tiny helper to save a cleaned table and report what we saved
def save_clean(df, name):
    df.to_csv(os.path.join(clean_folder, name), index=False)
    print(f"  saved {name}: {df.shape[0]} rows, {df.shape[1]} cols")


print("Loading raw tables...")
customers = load_raw("olist_customers_dataset.csv")
orders = load_raw("olist_orders_dataset.csv")
order_items = load_raw("olist_order_items_dataset.csv")
order_payments = load_raw("olist_order_payments_dataset.csv")
order_reviews = load_raw("olist_order_reviews_dataset.csv")
products = load_raw("olist_products_dataset.csv")
sellers = load_raw("olist_sellers_dataset.csv")
geolocation = load_raw("olist_geolocation_dataset.csv")
translation = load_raw("product_category_name_translation.csv")


# ---- ORDERS: turn the text timestamps into real dates ----
print("Cleaning orders (parsing timestamps)...")
order_date_cols = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]
for col in order_date_cols:
    # coerce keeps the meaningful nulls as NaT instead of erroring out
    orders[col] = pd.to_datetime(orders[col], errors="coerce")


# ---- ORDER_ITEMS: one date column here ----
print("Cleaning order_items...")
order_items["shipping_limit_date"] = pd.to_datetime(
    order_items["shipping_limit_date"], errors="coerce"
)


# ---- ORDER_REVIEWS: two date columns ----
print("Cleaning order_reviews...")
for col in ["review_creation_date", "review_answer_timestamp"]:
    order_reviews[col] = pd.to_datetime(order_reviews[col], errors="coerce")


# ---- PRODUCTS: translate categories, label the blanks ----
print("Cleaning products (translating categories)...")
# label the 610 missing portuguese categories first
products["product_category_name"] = products["product_category_name"].fillna("unknown")
# bring in the english name from the translation lookup
products = products.merge(translation, on="product_category_name", how="left")
# anything with no english match (including our 'unknown') becomes 'unknown'
products["product_category_name_english"] = products[
    "product_category_name_english"
].fillna("unknown")


# ---- GEOLOCATION: collapse duplicates to one row per zip prefix ----
print("Cleaning geolocation (deduping to one row per zip prefix)...")
geo_clean = (
    geolocation.groupby("geolocation_zip_code_prefix")
    .agg(
        geolocation_lat=("geolocation_lat", "mean"),
        geolocation_lng=("geolocation_lng", "mean"),
        geolocation_city=("geolocation_city", "first"),
        geolocation_state=("geolocation_state", "first"),
    )
    .reset_index()
)


# customers, sellers, order_payments are already clean, they pass through as-is

print("\nSaving cleaned tables to data/clean ...")
save_clean(customers, "customers.csv")
save_clean(orders, "orders.csv")
save_clean(order_items, "order_items.csv")
save_clean(order_payments, "order_payments.csv")
save_clean(order_reviews, "order_reviews.csv")
save_clean(products, "products.csv")
save_clean(sellers, "sellers.csv")
save_clean(geo_clean, "geolocation.csv")

# quick sanity check
missing_cat = (products["product_category_name_english"] == "unknown").sum()
print("\nETL done. Cleaned tables are in data/clean/")
print("products labelled 'unknown' category:", missing_cat)