"""
kpi_analysis.py
----------------
Handbook Chapter 7.6 / 8.6 (Business KPI Calculations).

Computes the same 15 business case studies solved in SQL
(SQL/advanced_queries.sql), this time using Pandas — the way an
analyst would once the data is already sitting in a DataFrame rather
than a live database. Each function returns a small, clean DataFrame
that visualization.py turns into a chart and Chapter 11's insight
framework turns into a written recommendation.
"""

import os
import numpy as np
import pandas as pd

OUTPUT_RESULTS = os.path.join(os.path.dirname(__file__), "..", "Output", "Results")


# CS1 — Monthly revenue trend
def kpi_monthly_revenue(rentals):
    return (rentals.groupby("rental_month")
            .agg(total_rentals=("rental_id", "count"),
                 total_revenue=("total_amount", "sum"),
                 avg_rental_value=("total_amount", "mean"))
            .round(2).reset_index().sort_values("rental_month"))


# CS2 — Revenue & duration by vehicle category
def kpi_revenue_by_category(rentals):
    return (rentals.groupby("category_name")
            .agg(total_rentals=("rental_id", "count"),
                 total_revenue=("total_amount", "sum"),
                 avg_duration_days=("rental_days", "mean"))
            .round(2).reset_index().sort_values("total_revenue", ascending=False))


# CS3 — Top 10 most-rented vehicles
def kpi_top_vehicles(rentals):
    return (rentals.groupby(["vehicle_id", "make", "model", "category_name"])
            .agg(times_rented=("rental_id", "count"),
                 revenue_generated=("total_amount", "sum"))
            .round(2).reset_index()
            .sort_values("times_rented", ascending=False).head(10))


# CS4 — Revenue by branch/location
def kpi_revenue_by_location(rentals):
    return (rentals.groupby(["pickup_location", "pickup_city"])
            .agg(total_rentals=("rental_id", "count"),
                 total_revenue=("total_amount", "sum"),
                 avg_rental_value=("total_amount", "mean"))
            .round(2).reset_index().sort_values("total_revenue", ascending=False))


# CS5 — Membership tier performance
def kpi_membership_performance(rentals):
    g = rentals.groupby("membership_type").agg(
        customers=("customer_id", "nunique"),
        total_rentals=("rental_id", "count"),
        total_revenue=("total_amount", "sum"))
    g["rentals_per_customer"] = (g["total_rentals"] / g["customers"]).round(2)
    g["avg_spend_per_customer"] = (g["total_revenue"] / g["customers"]).round(2)
    return g.round(2).reset_index().sort_values("avg_spend_per_customer", ascending=False)


# CS6 — Revenue share by category (adds % of total using a vectorised op)
def kpi_category_revenue_share(rentals):
    g = rentals.groupby("category_name")["total_amount"].sum().round(2)
    share = (100 * g / g.sum()).round(2)
    out = pd.DataFrame({"category_revenue": g, "pct_of_total_revenue": share})
    return out.reset_index().sort_values("category_revenue", ascending=False)


# CS7 — Late return rate by category
def kpi_late_returns_by_category(rentals):
    g = rentals.groupby("category_name").agg(
        total_completed=("rental_id", "count"),
        late_returns=("is_late_return", "sum"))
    g["late_return_pct"] = (100 * g["late_returns"] / g["total_completed"]).round(2)
    return g.reset_index().sort_values("late_return_pct", ascending=False)


# CS8 — Net contribution per vehicle after maintenance cost
def kpi_vehicle_net_contribution(rentals, maintenance):
    revenue = rentals.groupby("vehicle_id")["total_amount"].sum()
    maint_cost = maintenance.groupby("vehicle_id")["cost"].sum()
    vehicle_info = rentals[["vehicle_id", "make", "model"]].drop_duplicates("vehicle_id")
    out = vehicle_info.set_index("vehicle_id")
    out["rental_revenue"] = revenue
    out["maintenance_cost"] = maint_cost
    out = out.fillna(0)
    out["net_contribution"] = out["rental_revenue"] - out["maintenance_cost"]
    return out.reset_index().sort_values("net_contribution").head(10)


# CS9 — Seasonal demand by month
def kpi_seasonal_demand(rentals):
    order = ["January", "February", "March", "April", "May", "June", "July",
             "August", "September", "October", "November", "December"]
    g = (rentals.groupby("month_name")
         .agg(total_rentals=("rental_id", "count"),
              total_revenue=("total_amount", "sum"))
         .reindex(order).round(2).reset_index())
    return g


# CS10 — Revenue & rentals by fuel type
def kpi_fuel_type_analysis(rentals):
    return (rentals.groupby("fuel_type")
            .agg(total_rentals=("rental_id", "count"),
                 total_revenue=("total_amount", "sum"),
                 avg_revenue_per_rental=("total_amount", "mean"))
            .round(2).reset_index().sort_values("total_revenue", ascending=False))


# CS11 — Age group vs category preference
def kpi_age_group_category(rentals, customers):
    merged = rentals.merge(customers[["customer_id", "age_group"]], on="customer_id", how="left")
    return (merged.groupby(["age_group", "category_name"], observed=True)
            .size().reset_index(name="total_rentals")
            .sort_values(["age_group", "total_rentals"], ascending=[True, False]))


# CS12 — Payment method mix & failure rate
def kpi_payment_analysis(payments):
    g = payments.groupby("payment_method").agg(
        total_payments=("payment_id", "count"),
        failed_payments=("payment_status", lambda s: (s == "Failed").sum()),
        revenue_collected=("amount", lambda s: s[payments.loc[s.index, "payment_status"] == "Success"].sum()))
    g["failed_pct"] = (100 * g["failed_payments"] / g["total_payments"]).round(2)
    return g.round(2).reset_index().sort_values("total_payments", ascending=False)


# CS13 — Maintenance downtime leaderboard
def kpi_maintenance_downtime(maintenance):
    return (maintenance.groupby(["vehicle_id", "make", "model", "category_name"])
            .agg(maintenance_events=("maintenance_id", "count"),
                 total_downtime_days=("downtime_days", "sum"),
                 total_maintenance_cost=("cost", "sum"))
            .round(2).reset_index()
            .sort_values("total_downtime_days", ascending=False).head(10))


# CS14 — Top 10 customers by lifetime value (rank via pandas)
def kpi_top_customers(rentals):
    g = (rentals.groupby(["customer_id", "customer_name", "membership_type"])["total_amount"]
         .sum().reset_index().rename(columns={"total_amount": "total_spend"}))
    g["customer_rank"] = g["total_spend"].rank(ascending=False, method="min").astype(int)
    return g.sort_values("customer_rank").head(10)


# CS15 — Branch-level fleet utilization (rented-days per vehicle)
def kpi_branch_utilization(rentals, vehicles):
    fleet_size = vehicles.groupby(["location_name", "city"])["vehicle_id"].nunique()
    rented_days = rentals.groupby(["pickup_location", "pickup_city"])["rental_days"].sum()
    rental_count = rentals.groupby(["pickup_location", "pickup_city"])["rental_id"].count()

    out = pd.DataFrame({"fleet_size": fleet_size})
    out.index.names = ["pickup_location", "pickup_city"]
    out["total_rentals"] = rental_count
    out["total_rented_days"] = rented_days
    out = out.fillna(0)
    out["rented_days_per_vehicle"] = (out["total_rented_days"] / out["fleet_size"]).round(2)
    return out.reset_index().sort_values("rented_days_per_vehicle", ascending=False)


def run_all_kpis(cleaned_data: dict, save_csv=True) -> dict:
    rentals = cleaned_data["rentals"]
    vehicles = cleaned_data["vehicles"]
    customers = cleaned_data["customers"]
    payments = cleaned_data["payments"]
    maintenance = cleaned_data["maintenance"]

    results = {
        "01_monthly_revenue": kpi_monthly_revenue(rentals),
        "02_revenue_by_category": kpi_revenue_by_category(rentals),
        "03_top_vehicles": kpi_top_vehicles(rentals),
        "04_revenue_by_location": kpi_revenue_by_location(rentals),
        "05_membership_performance": kpi_membership_performance(rentals),
        "06_category_revenue_share": kpi_category_revenue_share(rentals),
        "07_late_returns_by_category": kpi_late_returns_by_category(rentals),
        "08_vehicle_net_contribution": kpi_vehicle_net_contribution(rentals, maintenance),
        "09_seasonal_demand": kpi_seasonal_demand(rentals),
        "10_fuel_type_analysis": kpi_fuel_type_analysis(rentals),
        "11_age_group_category": kpi_age_group_category(rentals, customers),
        "12_payment_analysis": kpi_payment_analysis(payments),
        "13_maintenance_downtime": kpi_maintenance_downtime(maintenance),
        "14_top_customers": kpi_top_customers(rentals),
        "15_branch_utilization": kpi_branch_utilization(rentals, vehicles),
    }

    if save_csv:
        os.makedirs(OUTPUT_RESULTS, exist_ok=True)
        for name, df in results.items():
            df.to_csv(os.path.join(OUTPUT_RESULTS, f"{name}.csv"), index=False)
        print(f"All 15 KPI result tables saved to {OUTPUT_RESULTS}")

    return results


if __name__ == "__main__":
    from data_loader import load_all_data
    from data_cleaning import full_cleaning_pipeline

    raw = load_all_data()
    cleaned = full_cleaning_pipeline(raw)
    kpis = run_all_kpis(cleaned)
    for name, df in kpis.items():
        print(f"\n--- {name} ---")
        print(df.head())
