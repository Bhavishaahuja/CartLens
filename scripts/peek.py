import pandas as pd
import os

data_folder = "data"

# make sure the folder is actually there before we do anything
if not os.path.isdir(data_folder):
    print("PROBLEM: no folder called", data_folder, "here:", os.getcwd())
    raise SystemExit

# grab every csv in the folder
csv_files = [f for f in os.listdir(data_folder) if f.endswith(".csv")]

# if the folder exists but is empty, say so out loud
if len(csv_files) == 0:
    print("PROBLEM: found the folder but no CSVs inside it")
    raise SystemExit

print("Found", len(csv_files), "csv files. Reading each one...\n")

for filename in csv_files:
    full_path = os.path.join(data_folder, filename)
    df = pd.read_csv(full_path)

    print("=" * 70)
    print("FILE:", filename)
    print("rows, columns:", df.shape)
    print("-" * 70)

    # each column, its type, and how many values are missing
    for col in df.columns:
        null_count = df[col].isnull().sum()
        print(f"  {col:<40} {str(df[col].dtype):<12} nulls: {null_count}")

    # a couple of real rows so we can eyeball the data
    print("-" * 70)
    print(df.head(2).to_string())
    print()