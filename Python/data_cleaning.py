"""
data_cleaning.py
-----------------
Handbook Chapter 8.2 (Data Cleaning), 8.3 (Data Validation), and
8.4 (Feature Engineering).

Takes the raw DataFrames produced by data_loader.py and returns
clean, analysis-ready DataFrames with the extra engineered columns
used throughout eda.py, kpi_analysis.py, and visualization.py.
"""

import pandas as pd
import numpy as np
from datetime import date


# ---------------------------------------------------------------------
# 8.2 DATA CLEANING
# ---------------------------------------------------------------------
def clean_rentals(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans the completed-rentals DataFrame (from vw_completed_rentals)."""
    df = df.copy()

    # --- missing values ---
    before = len(df)
    missing_report = df.isnull().sum()
    critical_cols = ["rental_id", "vehicle_id", "customer_id", "pickup_date", "total_amount"]
    df = df.dropna(subset=critical_cols)
    dropped_missing = before - len(df)

    # --- duplicates ---
    before = len(df)
    df = df.drop_duplicates(subset="rental_id")
    dropped_dupes = before - len(df)

    # --- data types ---
    date_cols = ["pickup_date", "expected_return_date", "actual_return_date"]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce")
    df["rental_days"] = pd.to_numeric(df["rental_days"], errors="coerce")

    # --- standardise text values ---
    text_cols = ["category_name", "membership_type", "gender", "fuel_type", "transmission"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()

    # rows where actual_return_date ended up null after coercion, or where
    # rental_days came out negative/zero due to a bad date, are not usable
    df = df[df["actual_return_date"].notna()]
    df = df[df["rental_days"] >= 0]

    print(f"[clean_rentals] Dropped {dropped_missing} rows with missing critical fields, "
          f"{dropped_dupes} duplicate rentals. Final shape: {df.shape}")
    return df.reset_index(drop=True)


def clean_vehicles(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.drop_duplicates(subset="vehicle_id")
    df["daily_rate"] = pd.to_numeric(df["daily_rate"], errors="coerce")
    df["purchase_date"] = pd.to_datetime(df["purchase_date"], errors="coerce")
    df["category_name"] = df["category_name"].astype(str).str.strip().str.title()
    df["status"] = df["status"].astype(str).str.strip().str.title()
    df = df[df["daily_rate"] > 0]
    return df.reset_index(drop=True)


def clean_payments(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.drop_duplicates(subset="payment_id")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    df["payment_date"] = pd.to_datetime(df["payment_date"], errors="coerce")
    df["payment_status"] = df["payment_status"].astype(str).str.strip().str.title()
    df["payment_method"] = df["payment_method"].astype(str).str.strip().str.title()
    return df.reset_index(drop=True)


def clean_maintenance(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.drop_duplicates(subset="maintenance_id")
    df["cost"] = pd.to_numeric(df["cost"], errors="coerce").fillna(0)
    df["downtime_days"] = pd.to_numeric(df["downtime_days"], errors="coerce").fillna(0)
    df["maintenance_date"] = pd.to_datetime(df["maintenance_date"], errors="coerce")
    df["maintenance_type"] = df["maintenance_type"].astype(str).str.strip().str.title()
    df = df[df["cost"] >= 0]
    return df.reset_index(drop=True)


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.drop_duplicates(subset="customer_id")
    df["date_of_birth"] = pd.to_datetime(df["date_of_birth"], errors="coerce")
    df["join_date"] = pd.to_datetime(df["join_date"], errors="coerce")
    df["gender"] = df["gender"].astype(str).str.strip().str.title()
    df["membership_type"] = df["membership_type"].astype(str).str.strip().str.title()
    return df.reset_index(drop=True)


# ---------------------------------------------------------------------
# 8.3 DATA VALIDATION
# ---------------------------------------------------------------------
def validate_rentals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Logical sanity checks — not just formatting. Flags (rather than
    silently drops) rows that fail, so they can be reviewed.
    """
    issues = {}
    issues["return_before_pickup"] = (df["actual_return_date"] < df["pickup_date"]).sum()
    issues["negative_amount"] = (df["total_amount"] < 0).sum()
    issues["zero_amount_completed"] = (df["total_amount"] == 0).sum()

    for check, count in issues.items():
        status = "OK" if count == 0 else f"{count} rows flagged"
        print(f"[validate_rentals] {check}: {status}")

    # remove logically impossible rows (return before pickup)
    df = df[df["actual_return_date"] >= df["pickup_date"]].reset_index(drop=True)
    return df


# ---------------------------------------------------------------------
# 8.4 FEATURE ENGINEERING
# ---------------------------------------------------------------------
def engineer_rental_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["rental_month"] = df["pickup_date"].dt.to_period("M").astype(str)
    df["rental_year"] = df["pickup_date"].dt.year
    df["month_name"] = df["pickup_date"].dt.month_name()
    df["day_of_week"] = df["pickup_date"].dt.day_name()

    df["is_late_return"] = (df["actual_return_date"] > df["expected_return_date"]).astype(int)
    df["late_days"] = (df["actual_return_date"] - df["expected_return_date"]).dt.days.clip(lower=0)

    df["revenue_per_day"] = np.where(df["rental_days"] > 0,
                                      df["total_amount"] / df["rental_days"], df["total_amount"])
    return df


def engineer_customer_features(customers_df: pd.DataFrame, reference_date=None) -> pd.DataFrame:
    df = customers_df.copy()
    ref = pd.Timestamp(reference_date) if reference_date else pd.Timestamp(date.today())
    df["age"] = ((ref - df["date_of_birth"]).dt.days // 365).astype(int)
    df["age_group"] = pd.cut(
        df["age"], bins=[0, 30, 45, 60, 120],
        labels=["21-30", "31-45", "46-60", "60+"]
    )
    df["tenure_years"] = ((ref - df["join_date"]).dt.days / 365).round(1)
    return df


def full_cleaning_pipeline(raw_data: dict) -> dict:
    """Runs the complete clean -> validate -> feature-engineer pipeline
    on every raw DataFrame and returns the analysis-ready dict."""
    clean = {}
    clean["rentals"] = clean_rentals(raw_data["rentals"])
    clean["rentals"] = validate_rentals(clean["rentals"])
    clean["rentals"] = engineer_rental_features(clean["rentals"])

    clean["vehicles"] = clean_vehicles(raw_data["vehicles"])
    clean["payments"] = clean_payments(raw_data["payments"])
    clean["maintenance"] = clean_maintenance(raw_data["maintenance"])
    clean["customers"] = engineer_customer_features(clean_customers(raw_data["customers"]))
    clean["locations"] = raw_data["locations"].copy()

    return clean


if __name__ == "__main__":
    from data_loader import load_all_data
    raw = load_all_data()
    cleaned = full_cleaning_pipeline(raw)
    for name, df in cleaned.items():
        print(f"{name}: cleaned shape {df.shape}")
