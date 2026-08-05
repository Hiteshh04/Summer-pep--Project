"""
data_loader.py
--------------
Loads data directly from CSV files instead of MySQL.
"""

from pathlib import Path
import pandas as pd

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Folder containing cleaned CSV files
DATA_DIR = BASE_DIR / "Data" / "cleaned"


def load_all_data():
    """
    Loads all cleaned CSV files and returns a dictionary of DataFrames.
    """

    data = {}

    data["rentals"] = pd.read_csv(
    DATA_DIR / "rentals_cleaned.csv",
    parse_dates=["pickup_date", "dropoff_date"]
)

data["vehicles"] = pd.read_csv(DATA_DIR / "vehicles_cleaned.csv")

data["customers"] = pd.read_csv(DATA_DIR / "customers_cleaned.csv")

data["payments"] = pd.read_csv(DATA_DIR / "payments_cleaned.csv")

data["maintenance"] = pd.read_csv(DATA_DIR / "maintenance_cleaned.csv")

data["locations"] = pd.read_csv(DATA_DIR / "locations_cleaned.csv")

if __name__ == "__main__":
    all_data = load_all_data()

    for name, df in all_data.items():
        print(f"{name}: {df.shape[0]} rows, {df.shape[1]} columns")