"""
Download and load the UCI "Diabetes 130-US Hospitals for Years 1999-2008" dataset.

Run from the repo root:
    .venv\\Scripts\\python.exe 01-healthcare-data-analysis/src/data_loader.py
"""

import csv
import io
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd
from ucimlrepo import fetch_ucirepo

# ID of this dataset on the UCI Machine Learning Repository website
UCI_DATASET_ID = 296

# The full zip on UCI also contains IDS_mapping.csv, which explains what
# the numbers in the *_id columns mean. ucimlrepo does not include it.
UCI_ZIP_URL = (
    "https://archive.ics.uci.edu/static/public/296/"
    "diabetes+130-us+hospitals+for+years+1999-2008.zip"
)

# Build file paths from this script's location, so they work
# no matter which folder you run the code from.
# __file__ = .../src/data_loader.py, so .parent.parent = the project folder
PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = PROJECT_DIR / "data" / "raw" / "diabetic_data.csv"
ID_MAPPING_PATH = PROJECT_DIR / "data" / "raw" / "IDS_mapping.csv"


def download_diabetes_data(save_path=RAW_DATA_PATH):
    """Download the dataset and save it as a CSV file.

    If the file already exists, skip the download and return the path.
    """
    save_path = Path(save_path)

    # Step 1: don't download again if we already have the file
    if save_path.exists():
        print(f"File already exists, skipping download: {save_path}")
        return save_path

    # Step 2: download the dataset from UCI
    print("Downloading dataset from UCI (this can take a few minutes)...")
    dataset = fetch_ucirepo(id=UCI_DATASET_ID)

    # 'original' is the full table: ID columns + features + target column
    df = dataset.data.original

    # Step 3: make sure the data/raw folder exists, then save the CSV
    save_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(save_path, index=False)  # index=False: don't write row numbers

    print(f"Saved {len(df):,} rows and {len(df.columns)} columns to {save_path}")
    return save_path


def download_id_mapping(save_path=ID_MAPPING_PATH):
    """Download IDS_mapping.csv from the official UCI zip file.

    If the file already exists, skip the download and return the path.
    """
    save_path = Path(save_path)

    if save_path.exists():
        print(f"File already exists, skipping download: {save_path}")
        return save_path

    print("Downloading ID mapping file from UCI...")
    # Download the zip into memory, then pull out just the one file we need
    with urllib.request.urlopen(UCI_ZIP_URL, timeout=120) as response:
        zip_bytes = response.read()

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zip_file:
        mapping_bytes = zip_file.read("IDS_mapping.csv")

    save_path.parent.mkdir(parents=True, exist_ok=True)
    save_path.write_bytes(mapping_bytes)

    print(f"Saved ID mapping to {save_path}")
    return save_path


def load_raw_data(path=RAW_DATA_PATH):
    """Read the raw CSV into a pandas DataFrame, exactly as it is on disk.

    low_memory=False makes pandas read the whole file before guessing each
    column's type, which avoids a "mixed types" warning.
    """
    return pd.read_csv(path, low_memory=False)


def load_id_mappings(path=ID_MAPPING_PATH):
    """Read IDS_mapping.csv into a dictionary of dictionaries.

    The file is three small tables stacked on top of each other, separated
    by blank lines. Each table starts with a header like
    "admission_type_id,description". The result looks like:

        {"admission_type_id": {1: "Emergency", 2: "Urgent", ...},
         "discharge_disposition_id": {...},
         "admission_source_id": {...}}
    """
    mappings = {}
    current_table = None

    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            # Skip blank separator lines (they look like ",")
            if not row or row[0].strip() == "":
                continue

            id_value = row[0].strip()
            description = row[1].strip()

            # A header line starts a new table
            if description == "description":
                current_table = id_value
                mappings[current_table] = {}
            else:
                mappings[current_table][int(id_value)] = description

    return mappings


# This block only runs when you run the file directly,
# not when you import the functions into a notebook.
if __name__ == "__main__":
    download_diabetes_data()
    download_id_mapping()
