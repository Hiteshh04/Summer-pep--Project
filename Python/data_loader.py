"""
data_loader.py
--------------
Handbook Chapter 8.1 (Data Extraction).

Centralises every SQL query used to pull data out of MySQL into a
Pandas DataFrame, so every other script imports from here instead of
repeating queries.
"""

import pandas as pd
from db_connection import get_connection, close_connection


def load_all_data():
    """
    Connects to MySQL, pulls every table/view needed for the analysis,
    closes the connection, and returns a dictionary of DataFrames.
    """
    connection = get_connection()

    data = {}

    # Main analytical dataset: one row per completed rental, already
    # joined with vehicle, category, customer, and location dimensions
    # via the vw_completed_rentals view created in advanced_queries.sql.
    data["rentals"] = pd.read_sql("SELECT * FROM vw_completed_rentals", connection)

    data["vehicles"] = pd.read_sql("""
        SELECT v.*, vc.category_name, l.location_name, l.city
        FROM vehicles v
        JOIN vehicle_categories vc ON v.category_id = vc.category_id
        JOIN locations l ON v.home_location_id = l.location_id
    """, connection)

    data["customers"] = pd.read_sql("SELECT * FROM customers", connection)

    data["payments"] = pd.read_sql("""
        SELECT p.*, r.vehicle_id, r.customer_id, r.pickup_date
        FROM payments p
        JOIN rentals r ON p.rental_id = r.rental_id
    """, connection)

    data["maintenance"] = pd.read_sql("""
        SELECT m.*, v.make, v.model, vc.category_name
        FROM maintenance m
        JOIN vehicles v ON m.vehicle_id = v.vehicle_id
        JOIN vehicle_categories vc ON v.category_id = vc.category_id
    """, connection)

    data["locations"] = pd.read_sql("SELECT * FROM locations", connection)

    close_connection(connection)
    return data


if __name__ == "__main__":
    all_data = load_all_data()
    for name, df in all_data.items():
        print(f"{name}: {df.shape[0]} rows, {df.shape[1]} columns")
