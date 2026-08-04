"""
eda.py
------
Handbook Chapter 8.5 (Exploratory Data Analysis).

Open-ended exploration of the cleaned data: shape, summary statistics,
distributions, and value counts, before we commit to specific KPIs.
Findings are printed to console and also written to Output/Results/
so they can be referenced in the project report.
"""

import os
import pandas as pd

OUTPUT_RESULTS = os.path.join(os.path.dirname(__file__), "..", "Output", "Results")


def run_eda(cleaned_data: dict, save_report=True):
    rentals = cleaned_data["rentals"]
    vehicles = cleaned_data["vehicles"]
    customers = cleaned_data["customers"]
    payments = cleaned_data["payments"]
    maintenance = cleaned_data["maintenance"]

    lines = []

    def log(msg):
        print(msg)
        lines.append(str(msg))

    log("=" * 70)
    log("EXPLORATORY DATA ANALYSIS — Vehicle Utilization & Rental Analytics")
    log("=" * 70)

    log(f"\nRentals dataset shape: {rentals.shape}")
    log(f"Date range covered   : {rentals['pickup_date'].min().date()} to {rentals['pickup_date'].max().date()}")

    log("\n--- Rental amount summary statistics ---")
    log(rentals["total_amount"].describe().round(2))

    log("\n--- Rental duration (days) summary statistics ---")
    log(rentals["rental_days"].describe().round(2))

    log("\n--- Rentals by vehicle category ---")
    log(rentals["category_name"].value_counts())

    log("\n--- Rentals by membership type ---")
    log(rentals["membership_type"].value_counts())

    log("\n--- Late return rate overall ---")
    late_rate = rentals["is_late_return"].mean() * 100
    log(f"{late_rate:.2f}% of completed rentals were returned late")

    log("\n--- Vehicle fleet: status breakdown ---")
    log(vehicles["status"].value_counts())

    log("\n--- Vehicle fleet: category breakdown ---")
    log(vehicles["category_name"].value_counts())

    log("\n--- Customer age distribution ---")
    log(customers["age"].describe().round(1))

    log("\n--- Customer age group counts ---")
    log(customers["age_group"].value_counts())

    log("\n--- Payment status breakdown ---")
    log(payments["payment_status"].value_counts())

    log("\n--- Payment method breakdown ---")
    log(payments["payment_method"].value_counts())

    log("\n--- Maintenance type breakdown ---")
    log(maintenance["maintenance_type"].value_counts())

    log("\n--- Maintenance cost summary statistics ---")
    log(maintenance["cost"].describe().round(2))

    log("\n--- Correlation: rental_days vs total_amount ---")
    corr = rentals[["rental_days", "total_amount"]].corr().iloc[0, 1]
    log(f"Correlation coefficient: {corr:.3f}")

    if save_report:
        os.makedirs(OUTPUT_RESULTS, exist_ok=True)
        out_path = os.path.join(OUTPUT_RESULTS, "eda_findings.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(str(l) for l in lines))
        print(f"\nEDA findings saved to {out_path}")

    return rentals, vehicles, customers, payments, maintenance


if __name__ == "__main__":
    from data_loader import load_all_data
    from data_cleaning import full_cleaning_pipeline

    raw = load_all_data()
    cleaned = full_cleaning_pipeline(raw)
    run_eda(cleaned)
