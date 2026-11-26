"""
Download and load the CDC Diabetes Health Indicators dataset.

Source: UCI Machine Learning Repository, dataset id 891
https://archive.ics.uci.edu/dataset/891/cdc+diabetes+health+indicators

Run this file directly to download the data:
    python 02-diabetes-risk-prediction/src/data_loader.py
"""

from pathlib import Path

import pandas as pd
from ucimlrepo import fetch_ucirepo

# This file lives in src/, so the project folder is one level up.
# Building paths from here means the code works no matter where you run it from.
PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
RAW_DATA_PATH = RAW_DIR / "diabetes_health_indicators.csv"
VARIABLE_INFO_PATH = RAW_DIR / "variable_info.csv"

UCI_DATASET_ID = 891   # the id of this dataset on the UCI website


def load_diabetes_data(data_path=RAW_DATA_PATH, info_path=VARIABLE_INFO_PATH):
    """
    Return the dataset as a DataFrame.

    The first time, it downloads the data from UCI and saves two CSV files:
      - the data itself (one row per survey respondent)
      - the variable descriptions (what each column means)
    After that, it just reads the saved CSV, so we don't download it again.
    """
    # 1. If the file is already saved, skip the download
    if data_path.exists():
        print(f"Found saved data, loading {data_path.name}")
        return pd.read_csv(data_path)

    # 2. Otherwise download it from UCI (can take a minute)
    print("Downloading the CDC Diabetes Health Indicators dataset from UCI...")
    dataset = fetch_ucirepo(id=UCI_DATASET_ID)

    # .data.original holds every column (the ID, the features and the target) in one table
    df = dataset.data.original

    # .variables is a table describing each column (name, type, description...)
    variable_info = dataset.variables

    # 3. Save both files. mkdir makes the folder if it doesn't exist yet.
    data_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(data_path, index=False)
    variable_info.to_csv(info_path, index=False)
    print(f"Saved {len(df):,} rows to {data_path}")
    print(f"Saved variable descriptions to {info_path}")

    return df


# This block only runs when the file is run directly, not when it's imported
if __name__ == "__main__":
    data = load_diabetes_data()
    print(f"Shape: {data.shape[0]:,} rows x {data.shape[1]} columns")
    print(data.head())
