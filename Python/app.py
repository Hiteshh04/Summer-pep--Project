"""
app.py
------
Streamlit interactive dashboard for the Vehicle Utilization & Rental
Analytics project. Connects live to MySQL, cleans the data, computes
all 15 KPIs, and renders interactive Seaborn/Matplotlib charts with
sidebar filters (date range, branch, vehicle category, membership tier).

Run with:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

from data_loader import load_all_data
from data_cleaning import full_cleaning_pipeline
import kpi_analysis as kpi

sns.set_style("whitegrid")

st.set_page_config(page_title="Vehicle Rental Analytics", layout="wide", page_icon="🚗")


# ---------------------------------------------------------------------
# DATA LOADING (cached so we don't hit MySQL on every filter change)
# ---------------------------------------------------------------------
@st.cache_data(show_spinner="Loading CSV data...")
def get_cleaned_data():
    raw = load_all_data()
    cleaned = full_cleaning_pipeline(raw)
    return cleaned


st.title("🚗 Vehicle Utilization & Rental Analytics Dashboard")
st.caption("Vehicle Rental Analytics Dashboard (Offline CSV Dataset)")

try:
    data = get_cleaned_data()
except Exception as e:
    st.error(f"Error loading CSV data: {e}")
    st.stop()

rentals = data["rentals"]
vehicles = data["vehicles"]
customers = data["customers"]
payments = data["payments"]
maintenance = data["maintenance"]

# ---------------------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------------------
st.sidebar.header("Filters")

min_date, max_date = rentals["pickup_date"].min(), rentals["pickup_date"].max()
date_range = st.sidebar.date_input("Pickup date range", (min_date, max_date),
                                    min_value=min_date, max_value=max_date)

categories = sorted(rentals["category_name"].unique())
selected_categories = st.sidebar.multiselect("Vehicle category", categories, default=categories)

branches = sorted(rentals["pickup_location"].unique())
selected_branches = st.sidebar.multiselect("Branch", branches, default=branches)

memberships = sorted(rentals["membership_type"].unique())
selected_memberships = st.sidebar.multiselect("Membership tier", memberships, default=memberships)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start_date, end_date = min_date, max_date

mask = (
    rentals["pickup_date"].between(start_date, end_date)
    & rentals["category_name"].isin(selected_categories)
    & rentals["pickup_location"].isin(selected_branches)
    & rentals["membership_type"].isin(selected_memberships)
)
filtered = rentals[mask]

if filtered.empty:
    st.warning("No rentals match the selected filters. Try widening your date range or selections.")
    st.stop()

# ---------------------------------------------------------------------
# TOP-LEVEL KPI CARDS
# ---------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Revenue", f"₹{filtered['total_amount'].sum():,.0f}")
c2.metric("Total Rentals", f"{len(filtered):,}")
c3.metric("Avg Rental Value", f"₹{filtered['total_amount'].mean():,.0f}")
c4.metric("Late Return Rate", f"{filtered['is_late_return'].mean()*100:.1f}%")

st.divider()

# ---------------------------------------------------------------------
# TABS FOR EACH ANALYSIS AREA
# ---------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📈 Revenue & Trends", "🚙 Fleet & Categories", "👥 Customers",
     "🔧 Maintenance & Payments", "🏢 Branch Utilization"]
)

with tab1:
    st.subheader("Monthly Revenue Trend")
    monthly = kpi.kpi_monthly_revenue(filtered)
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=monthly, x="rental_month", y="total_revenue", marker="o", ax=ax, color="#3B5BA5")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M"))
    plt.xticks(rotation=75, fontsize=7)
    ax.set_xlabel("Month"); ax.set_ylabel("Revenue (₹)")
    st.pyplot(fig)

    st.subheader("Seasonal Demand by Month")
    seasonal = kpi.kpi_seasonal_demand(filtered)
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=seasonal, x="month_name", y="total_rentals", marker="o", ax=ax2, color="#B5651D")
    plt.xticks(rotation=45)
    ax2.set_xlabel("Month"); ax2.set_ylabel("Total Rentals")
    st.pyplot(fig2)

    with st.expander("View underlying data"):
        st.dataframe(monthly, width='stretch')

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Revenue by Category")
        cat_rev = kpi.kpi_revenue_by_category(filtered)
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(data=cat_rev, x="category_name", y="total_revenue", ax=ax, palette="mako", hue="category_name", legend=False)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M"))
        plt.xticks(rotation=30)
        st.pyplot(fig)
    with col2:
        st.subheader("Revenue Share by Category")
        share = kpi.kpi_category_revenue_share(filtered)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.pie(share["category_revenue"], labels=share["category_name"], autopct="%1.1f%%",
               colors=sns.color_palette("mako", len(share)), startangle=90)
        st.pyplot(fig)

    st.subheader("Top 10 Most-Rented Vehicles")
    top_v = kpi.kpi_top_vehicles(filtered)
    fig, ax = plt.subplots(figsize=(9, 5))
    labels = top_v["make"] + " " + top_v["model"] + " (#" + top_v["vehicle_id"].astype(str) + ")"
    sns.barplot(x=top_v["times_rented"], y=labels, ax=ax, palette="mako", hue=labels, legend=False)
    st.pyplot(fig)
    st.dataframe(top_v, width='stretch')

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Membership Tier Performance")
        mem = kpi.kpi_membership_performance(filtered)
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(data=mem, x="membership_type", y="avg_spend_per_customer", ax=ax, palette="mako", hue="membership_type", legend=False)
        st.pyplot(fig)
    with col2:
        st.subheader("Age Group vs Category Preference")
        age_cat = kpi.kpi_age_group_category(filtered, customers)
        pivot = age_cat.pivot(index="age_group", columns="category_name", values="total_rentals").fillna(0)
        fig, ax = plt.subplots(figsize=(6, 4))
        pivot.plot(kind="bar", stacked=True, ax=ax, colormap="viridis", legend=False)
        plt.xticks(rotation=0)
        st.pyplot(fig)

    st.subheader("Top 10 Customers by Lifetime Value")
    top_c = kpi.kpi_top_customers(filtered)
    st.dataframe(top_c, width='stretch')

with tab4:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Late Return Rate by Category")
        late = kpi.kpi_late_returns_by_category(filtered)
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(data=late, x="category_name", y="late_return_pct", ax=ax, palette="rocket", hue="category_name", legend=False)
        plt.xticks(rotation=30)
        st.pyplot(fig)
    with col2:
        st.subheader("Failed Payment Rate by Method")
        pay = kpi.kpi_payment_analysis(payments)
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(data=pay, x="payment_method", y="failed_pct", ax=ax, palette="rocket", hue="payment_method", legend=False)
        plt.xticks(rotation=20)
        st.pyplot(fig)

    st.subheader("Vehicles With Lowest Net Contribution (After Maintenance Cost)")
    net = kpi.kpi_vehicle_net_contribution(rentals, maintenance)
    st.dataframe(net, width='stretch')

with tab5:
    st.subheader("Fleet Utilization by Branch (Rented Days per Vehicle)")
    util = kpi.kpi_branch_utilization(rentals, vehicles)
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(data=util.sort_values("rented_days_per_vehicle", ascending=False),
                x="rented_days_per_vehicle", y="pickup_location", ax=ax, palette="mako", hue="pickup_location", legend=False)
    st.pyplot(fig)
    st.dataframe(util, width='stretch')

st.divider()
st.caption(
    "Data source: Offline CSV dataset · "
    "Built with Pandas, NumPy, Matplotlib, Seaborn, and Streamlit."
)
