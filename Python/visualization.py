"""
visualization.py
-----------------
Handbook Chapter 8.7 (Visualization) / Section 7.5 (Chart-type guidance).

Turns each KPI DataFrame from kpi_analysis.py into a saved chart image
in Output/Charts/, using the chart type that best fits the question
being asked (bar for category comparison, line for trend over time,
pie for share-of-whole, histogram for distribution, scatter for
relationships).
"""

import os
import matplotlib
matplotlib.use("Agg")  # safe for headless/script execution
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

sns.set_style("whitegrid")
PALETTE = "mako"

CHARTS_DIR = os.path.join(os.path.dirname(__file__), "..", "Output", "Charts")


def _save(fig, filename):
    os.makedirs(CHARTS_DIR, exist_ok=True)
    path = os.path.join(CHARTS_DIR, filename)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Saved chart: {path}")


def chart_monthly_revenue_trend(df):
    fig, ax = plt.subplots(figsize=(11, 5))
    sns.lineplot(data=df, x="rental_month", y="total_revenue", marker="o", ax=ax, color="#3B5BA5")
    ax.set_title("Monthly Revenue Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (₹)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M"))
    plt.xticks(rotation=75, fontsize=8)
    _save(fig, "01_monthly_revenue_trend.png")


def chart_revenue_by_category(df):
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=df.sort_values("total_revenue", ascending=False),
                x="category_name", y="total_revenue", ax=ax, palette=PALETTE, hue="category_name", legend=False)
    ax.set_title("Total Revenue by Vehicle Category")
    ax.set_xlabel("Category")
    ax.set_ylabel("Revenue (₹)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M"))
    _save(fig, "02_revenue_by_category.png")


def chart_top_vehicles(df):
    fig, ax = plt.subplots(figsize=(9, 6))
    labels = df["make"] + " " + df["model"] + " (#" + df["vehicle_id"].astype(str) + ")"
    sns.barplot(x=df["times_rented"], y=labels, ax=ax, palette=PALETTE, hue=labels, legend=False)
    ax.set_title("Top 10 Most-Rented Vehicles")
    ax.set_xlabel("Times Rented")
    ax.set_ylabel("Vehicle")
    _save(fig, "03_top_vehicles.png")


def chart_revenue_by_location(df):
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(data=df.sort_values("total_revenue", ascending=False),
                x="total_revenue", y="pickup_location", ax=ax, palette=PALETTE, hue="pickup_location", legend=False)
    ax.set_title("Total Revenue by Branch")
    ax.set_xlabel("Revenue (₹)")
    ax.set_ylabel("Branch")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M"))
    _save(fig, "04_revenue_by_location.png")


def chart_membership_performance(df):
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.barplot(data=df, x="membership_type", y="avg_spend_per_customer",
                ax=ax, palette=PALETTE, hue="membership_type", legend=False)
    ax.set_title("Average Spend per Customer by Membership Tier")
    ax.set_xlabel("Membership Tier")
    ax.set_ylabel("Avg Spend per Customer (₹)")
    _save(fig, "05_membership_performance.png")


def chart_category_revenue_share(df):
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(df["category_revenue"], labels=df["category_name"], autopct="%1.1f%%",
           colors=sns.color_palette(PALETTE, len(df)), startangle=90)
    ax.set_title("Revenue Share by Vehicle Category")
    _save(fig, "06_category_revenue_share.png")


def chart_late_returns_by_category(df):
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=df.sort_values("late_return_pct", ascending=False),
                x="category_name", y="late_return_pct", ax=ax, palette="rocket", hue="category_name", legend=False)
    ax.set_title("Late-Return Rate by Vehicle Category")
    ax.set_xlabel("Category")
    ax.set_ylabel("Late Return Rate (%)")
    _save(fig, "07_late_returns_by_category.png")


def chart_vehicle_net_contribution(df):
    fig, ax = plt.subplots(figsize=(9, 6))
    labels = df["make"] + " " + df["model"] + " (#" + df["vehicle_id"].astype(str) + ")"
    colors = ["#C0392B" if v < 0 else "#2E86C1" for v in df["net_contribution"]]
    ax.barh(labels, df["net_contribution"], color=colors)
    ax.set_title("Lowest Net Contribution After Maintenance Cost (Bottom 10 Vehicles)")
    ax.set_xlabel("Net Contribution (₹)")
    _save(fig, "08_vehicle_net_contribution.png")


def chart_seasonal_demand(df):
    fig, ax = plt.subplots(figsize=(11, 5))
    sns.lineplot(data=df, x="month_name", y="total_rentals", marker="o", ax=ax, color="#B5651D")
    ax.set_title("Seasonal Rental Demand by Month")
    ax.set_xlabel("Month")
    ax.set_ylabel("Total Rentals")
    plt.xticks(rotation=45)
    _save(fig, "09_seasonal_demand.png")


def chart_fuel_type_analysis(df):
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.barplot(data=df, x="fuel_type", y="total_revenue", ax=ax, palette=PALETTE, hue="fuel_type", legend=False)
    ax.set_title("Revenue by Fuel Type")
    ax.set_xlabel("Fuel Type")
    ax.set_ylabel("Revenue (₹)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M"))
    _save(fig, "10_fuel_type_analysis.png")


def chart_age_group_category(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    pivot = df.pivot(index="age_group", columns="category_name", values="total_rentals").fillna(0)
    pivot.plot(kind="bar", stacked=True, ax=ax, colormap="viridis")
    ax.set_title("Vehicle Category Preference by Customer Age Group")
    ax.set_xlabel("Age Group")
    ax.set_ylabel("Total Rentals")
    plt.xticks(rotation=0)
    ax.legend(title="Category", bbox_to_anchor=(1.02, 1), loc="upper left")
    _save(fig, "11_age_group_category.png")


def chart_payment_analysis(df):
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=df, x="payment_method", y="failed_pct", ax=ax, palette="rocket", hue="payment_method", legend=False)
    ax.set_title("Failed Payment Rate by Payment Method")
    ax.set_xlabel("Payment Method")
    ax.set_ylabel("Failed Payment Rate (%)")
    plt.xticks(rotation=20)
    _save(fig, "12_payment_analysis.png")


def chart_maintenance_downtime(df):
    fig, ax = plt.subplots(figsize=(9, 6))
    labels = df["make"] + " " + df["model"] + " (#" + df["vehicle_id"].astype(str) + ")"
    sns.barplot(x=df["total_downtime_days"], y=labels, ax=ax, palette="rocket", hue=labels, legend=False)
    ax.set_title("Top 10 Vehicles by Maintenance Downtime")
    ax.set_xlabel("Total Downtime (Days)")
    ax.set_ylabel("Vehicle")
    _save(fig, "13_maintenance_downtime.png")


def chart_top_customers(df):
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.barplot(x=df["total_spend"], y=df["customer_name"], ax=ax, palette=PALETTE, hue=df["customer_name"], legend=False)
    ax.set_title("Top 10 Customers by Lifetime Value")
    ax.set_xlabel("Total Spend (₹)")
    ax.set_ylabel("Customer")
    _save(fig, "14_top_customers.png")


def chart_branch_utilization(df):
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(data=df.sort_values("rented_days_per_vehicle", ascending=False),
                x="rented_days_per_vehicle", y="pickup_location", ax=ax, palette=PALETTE, hue="pickup_location", legend=False)
    ax.set_title("Fleet Utilization: Rented Days per Vehicle by Branch")
    ax.set_xlabel("Rented Days per Vehicle")
    ax.set_ylabel("Branch")
    _save(fig, "15_branch_utilization.png")


def generate_all_charts(kpi_results: dict):
    chart_monthly_revenue_trend(kpi_results["01_monthly_revenue"])
    chart_revenue_by_category(kpi_results["02_revenue_by_category"])
    chart_top_vehicles(kpi_results["03_top_vehicles"])
    chart_revenue_by_location(kpi_results["04_revenue_by_location"])
    chart_membership_performance(kpi_results["05_membership_performance"])
    chart_category_revenue_share(kpi_results["06_category_revenue_share"])
    chart_late_returns_by_category(kpi_results["07_late_returns_by_category"])
    chart_vehicle_net_contribution(kpi_results["08_vehicle_net_contribution"])
    chart_seasonal_demand(kpi_results["09_seasonal_demand"])
    chart_fuel_type_analysis(kpi_results["10_fuel_type_analysis"])
    chart_age_group_category(kpi_results["11_age_group_category"])
    chart_payment_analysis(kpi_results["12_payment_analysis"])
    chart_maintenance_downtime(kpi_results["13_maintenance_downtime"])
    chart_top_customers(kpi_results["14_top_customers"])
    chart_branch_utilization(kpi_results["15_branch_utilization"])
    print(f"\nAll 15 charts saved to {CHARTS_DIR}")


if __name__ == "__main__":
    from data_loader import load_all_data
    from data_cleaning import full_cleaning_pipeline
    from kpi_analysis import run_all_kpis

    raw = load_all_data()
    cleaned = full_cleaning_pipeline(raw)
    kpis = run_all_kpis(cleaned)
    generate_all_charts(kpis)
