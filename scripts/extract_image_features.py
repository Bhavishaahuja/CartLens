import os
import random
import numpy as np
from PIL import Image
from scipy import ndimage
from sklearn.cluster import KMeans
import pandas as pd

# where the category folders live (mind the space in the folder name)
image_root = os.path.join("images", "ecommerce products")

# how many images to sample per category so this runs fast
sample_per_category = 250

# map this image set's categories onto Olist's english category names.
# this is a category-level enrichment join, and we say so in the README.
category_map = {
    "tshirt": "fashion_male_clothing",
    "jeans": "fashion_male_clothing",
    "sofa": "furniture_decor",
    "tv": "electronics",
}

# seed so the random sample is the same every run
random.seed(42)

# we collect one dict per image, then turn the whole thing into a table
all_rows = []

image_exts = (".jpg", ".jpeg", ".png")

# walk each category folder one at a time
for folder_name in os.listdir(image_root):
    folder_path = os.path.join(image_root, folder_name)

    # skip anything that isn't actually a folder
    if not os.path.isdir(folder_path):
        continue

    # gather the image files sitting in this category
    files_here = []
    for f in os.listdir(folder_path):
        if f.lower().endswith(image_exts):
            files_here.append(f)

    # take a random sample so we're not chewing through everything
    if len(files_here) > sample_per_category:
        files_here = random.sample(files_here, sample_per_category)

    print(f"{folder_name}: processing {len(files_here)} images")

    for file_name in files_here:
        file_path = os.path.join(folder_path, file_name)

        # broken images happen, so guard the read
        try:
            img = Image.open(file_path).convert("RGB")
        except Exception:
            print("  skipped (couldn't open):", file_name)
            continue

        width, height = img.size
        aspect_ratio = round(width / height, 3)

        # brightness: average pixel value on a grayscale copy (0 dark, 255 bright)
        gray_array = np.array(img.convert("L"))
        brightness = round(float(gray_array.mean()), 2)

        # blur/sharpness: variance of the Laplacian.
        # sharp photos have lots of edge detail (high variance), blurry ones are smooth (low)
        laplacian = ndimage.laplace(gray_array.astype(float))
        blur_score = round(float(laplacian.var()), 2)

        # dominant color: shrink the image, cluster the pixels, take the biggest cluster
        small = img.resize((60, 60))
        pixels = np.array(small).reshape(-1, 3)
        kmeans = KMeans(n_clusters=3, n_init=10, random_state=42)
        labels = kmeans.fit_predict(pixels)
        counts = np.bincount(labels)
        biggest_cluster = counts.argmax()
        dom_color = kmeans.cluster_centers_[biggest_cluster]

        row = {
            "image_file": file_name,
            "image_category": folder_name,
            "olist_category": category_map.get(folder_name, "unknown"),
            "width_px": width,
            "height_px": height,
            "aspect_ratio": aspect_ratio,
            "brightness": brightness,
            "blur_score": blur_score,
            "dominant_r": int(dom_color[0]),
            "dominant_g": int(dom_color[1]),
            "dominant_b": int(dom_color[2]),
        }
        all_rows.append(row)

# fold all the rows into one table and save it next to the other data
features = pd.DataFrame(all_rows)
output_path = os.path.join("data", "product_image_features.csv")
features.to_csv(output_path, index=False)

print()
print("Done. Wrote", len(features), "rows to", output_path)
print(features.head())