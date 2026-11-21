"""
Download the UCI "Diabetes 130-US Hospitals for Years 1999-2008" dataset.

Run from the project folder:
    python src/data_loader.py
"""

from pathlib import Path

from ucimlrepo import fetch_ucirepo

# ID of this dataset on the UCI Machine Learning Repository website
UCI_DATASET_ID = 296

# Build the file path from this script's location, so it works
# no matter which folder you run the script from.
# __file__ = .../src/data_loader.py, so .parent.parent = the project folder
PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = PROJECT_DIR / "data" / "raw" / "diabetic_data.csv"


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
    print("Downloading dataset from UCI (this can take a minute)...")
    dataset = fetch_ucirepo(id=UCI_DATASET_ID)

    # 'original' is the full table: ID columns + features + target column
    df = dataset.data.original

    # Step 3: make sure the data/raw folder exists, then save the CSV
    save_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(save_path, index=False)  # index=False: don't write row numbers

    print(f"Saved {len(df):,} rows and {len(df.columns)} columns to {save_path}")
    return save_path


# This block only runs when you run the file directly,
# not when you import the function into a notebook.
if __name__ == "__main__":
    download_diabetes_data()
