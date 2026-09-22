from google.cloud import storage
import os

project_id = "cartlens-509400"
bucket_name = "cartlens-images"

# uses the same application-default credentials as the BigQuery load
client = storage.Client(project=project_id)
bucket = client.bucket(bucket_name)

image_root = os.path.join("images", "ecommerce products")
image_exts = (".jpg", ".jpeg", ".png")

uploaded = 0
# walk each category folder and push every image up
for folder_name in os.listdir(image_root):
    folder_path = os.path.join(image_root, folder_name)
    if not os.path.isdir(folder_path):
        continue

    for file_name in os.listdir(folder_path):
        if not file_name.lower().endswith(image_exts):
            continue

        local_path = os.path.join(folder_path, file_name)
        # keep the category folder structure inside the bucket
        blob_name = f"{folder_name}/{file_name}"
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(local_path)

        uploaded += 1
        if uploaded % 100 == 0:
            print(f"  uploaded {uploaded} images...")

print(f"\nDone. Uploaded {uploaded} images to gs://{bucket_name}/")