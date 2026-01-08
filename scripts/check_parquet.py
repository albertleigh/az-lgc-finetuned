import pandas as pd
from pathlib import Path

def check_parquet(file_path):
    print(f"Checking Parquet file: {file_path}")
    try:
        df = pd.read_parquet(file_path)
        print("✓ Successfully read Parquet file")
        print(f"DataFrame shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print("\nFirst 5 rows:")
        print(df.head())
        return True
    except Exception as e:
        print(f"✗ Error reading Parquet file: {e}")
        return False

if __name__ == "__main__":
    parquet_file = Path("datasets_dist/compare_training_dataset_20260104_150216.parquet")
    if parquet_file.exists():
        check_parquet(parquet_file)
    else:
        print(f"File not found: {parquet_file}")
