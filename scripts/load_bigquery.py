from google.cloud import bigquery

project_id = "cartlens-509400"
dataset_id = "cartlens"

# this picks up the credentials you set with the application-default login
client = bigquery.Client(project=project_id)

# each entry is (local csv file, the table name we want in BigQuery)
tables_to_load = [
    ("data/clean/customers.csv", "customers"),
    ("data/clean/orders.csv", "orders"),
    ("data/clean/order_items.csv", "order_items"),
    ("data/clean/order_payments.csv", "order_payments"),
    ("data/clean/order_reviews.csv", "order_reviews"),
    ("data/clean/products.csv", "products"),
    ("data/clean/sellers.csv", "sellers"),
    ("data/clean/geolocation.csv", "geolocation"),
    ("data/product_image_features.csv", "product_image_features"),
]

# how BigQuery should read each csv:
#  - figure out the column types itself (autodetect)
#  - skip the header row
#  - replace the table if it already exists, so re-running is safe
job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.CSV,
    autodetect=True,
    skip_leading_rows=1,
    allow_quoted_newlines=True,   # some review comments contain line breaks
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
)

for csv_path, table_name in tables_to_load:
    full_table_id = f"{project_id}.{dataset_id}.{table_name}"
    print(f"Loading {csv_path} -> {table_name} ...")

    with open(csv_path, "rb") as source_file:
        load_job = client.load_table_from_file(
            source_file, full_table_id, job_config=job_config
        )
    load_job.result()  # wait for the upload to finish before moving on

    # confirm how many rows actually landed
    loaded = client.get_table(full_table_id)
    print(f"  done: {loaded.num_rows} rows")

print("\nAll 9 tables are in BigQuery.")