"""
db_connection.py
-----------------
Handles the Python -> MySQL connection for the Vehicle Utilization &
Rental Analytics project (Handbook Chapter 6).

Credentials are NEVER hardcoded here. They are read from environment
variables (or a local .env file loaded with python-dotenv), so this
file is safe to commit to GitHub.

Usage:
    from db_connection import get_connection
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM vw_completed_rentals", conn)
    conn.close()
"""

import os
import sys
import mysql.connector
from mysql.connector import Error

try:
    from dotenv import load_dotenv
    load_dotenv()  # loads variables from a local .env file if present
except ImportError:
    # dotenv is optional; if it's not installed, we just rely on the
    # environment variables already being set (e.g. exported in the shell).
    pass


def get_connection():
    """
    Opens and returns a MySQL connection using credentials from
    environment variables:
        DB_HOST      (default: localhost)
        DB_USER      (default: root)
        DB_PASSWORD  (required)
        DB_NAME      (default: car_rental_analytics)

    Raises a clear error and exits if the connection fails, instead of
    crashing with a raw traceback.
    """
    config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "car_rental_analytics"),
    }

    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            print(f"Connected to MySQL database '{config['database']}' at {config['host']}")
        return connection
    except Error as e:
        print(f"ERROR: Could not connect to MySQL database. Details: {e}")
        print("Check that MySQL is running and DB_HOST/DB_USER/DB_PASSWORD/DB_NAME "
              "are set correctly (see .env.example).")
        sys.exit(1)


def close_connection(connection):
    """Closes a MySQL connection cleanly."""
    if connection is not None and connection.is_connected():
        connection.close()
        print("MySQL connection closed.")


if __name__ == "__main__":
    # Quick manual test: python db_connection.py
    conn = get_connection()
    close_connection(conn)
