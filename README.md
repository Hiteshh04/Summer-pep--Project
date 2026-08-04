# Vehicle Utilization & Rental Analytics

End-to-End Data Analytics Project — Car Rental Domain (SQL + Python)

## Overview

This project analyses a car rental business's operations end-to-end: from a
normalised MySQL database covering vehicles, customers, rentals, payments,
and maintenance, through a full Python analytics pipeline that cleans the
data, calculates business KPIs, visualises trends, and turns them into
written, decision-ready recommendations. An interactive Streamlit dashboard
lets a non-technical stakeholder explore every metric by date range,
branch, vehicle category, and membership tier.

## Tech Stack

MySQL, MySQL Workbench, Python, Pandas, NumPy, Matplotlib, Seaborn,
Streamlit, Jupyter Notebook (optional), Git, GitHub

## Project Structure

```
Vehicle-Rental-Analytics/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── SQL/
│   ├── schema.sql              -- 3NF schema: 8 tables, constraints, indexes
│   ├── sample_data.sql         -- ~13,000 realistic INSERT rows
│   └── advanced_queries.sql    -- 15 business case studies + views/procedure/trigger
├── Python/
│   ├── db_connection.py        -- MySQL connection (credentials via .env)
│   ├── data_loader.py          -- SQL extraction -> DataFrames
│   ├── data_cleaning.py        -- cleaning, validation, feature engineering
│   ├── eda.py                  -- exploratory data analysis
│   ├── kpi_analysis.py         -- all 15 business KPIs in Pandas
│   ├── visualization.py        -- Matplotlib/Seaborn charts -> Output/Charts
│   └── app.py                  -- Streamlit interactive dashboard
├── Data/
│   ├── raw/                    -- CSV snapshots exported from MySQL
│   └── cleaned/                -- cleaned data exports
├── Output/
│   ├── Charts/                 -- 15 saved chart images
│   └── Results/                -- 15 KPI result CSVs + eda_findings.txt
├── Reports/
│   └── project_report.md       -- full business problem -> recommendations report
├── Documentation/
│   └── er_diagram_notes.md     -- entity/relationship reference
├── Presentation/                -- put your slide deck here
└── Images/                      -- chart/screenshot exports for README/report
```

## Business Problem

A multi-city car rental company wants to understand which vehicles,
categories, and branches actually make it money once operating costs
(maintenance, downtime, late returns, failed payments) are accounted for —
and which customer segments are worth investing marketing effort in. This
project turns the company's transactional data into a decision-ready
analytics story addressing exactly that.

## Database Design

8 tables normalised to 3NF: `locations`, `vehicle_categories`, `vehicles`,
`customers`, `employees`, `rentals`, `payments`, `maintenance`. See
`Documentation/er_diagram_notes.md` for the full entity-relationship
reference, and export a visual ER diagram from MySQL Workbench
(Database → Reverse Engineer) to drop into that folder as an image.

## Key Analyses & KPIs (15 Business Case Studies)

1. Monthly revenue trend
2. Revenue & average duration by vehicle category
3. Top 10 most-rented vehicles
4. Revenue by branch/location
5. Membership-tier performance (rentals & spend per customer)
6. Revenue share by category
7. Late-return rate by category
8. Net contribution per vehicle after maintenance cost
9. Seasonal demand by month
10. Revenue & rentals by fuel type
11. Customer age group vs. category preference
12. Payment method mix & failed-payment rate
13. Maintenance downtime leaderboard
14. Top 10 customers by lifetime value
15. Branch-level fleet utilization (rented days per vehicle)

Every case study is solved twice — once in SQL (`SQL/advanced_queries.sql`)
and once independently in Pandas (`Python/kpi_analysis.py`) — so the two
results can be cross-checked against each other.

## Sample Insights

- **SUVs are the revenue leader**, generating ~30% of total revenue despite
  making up only ~26% of the fleet, ahead of Sedans and Luxury vehicles —
  a case for expanding SUV inventory before Luxury.
- **Late returns run at ~18% across all categories**, with Luxury vehicles
  slightly worse than the fleet average — a targeted late-fee or reminder
  policy for Luxury renters could recover meaningful revenue.
- **Platinum and Gold members spend more per rental but Silver-tier
  customers rent most frequently** — loyalty perks may be better aimed at
  converting Silver into Gold than acquiring new Platinum members.

See `Reports/project_report.md` for the full Observation → Reason →
Impact → Recommendation write-up on all major findings.

## How to Run This Project

1. Clone this repository.
2. Install dependencies: `pip install -r requirements.txt`
3. In MySQL Workbench (or CLI), run `SQL/schema.sql`, then
   `SQL/sample_data.sql`, then `SQL/advanced_queries.sql`.
4. Copy `.env.example` to `.env` and fill in your real MySQL credentials.
5. From the `Python/` folder, run the pipeline in order:
   ```
   python data_loader.py
   python data_cleaning.py
   python eda.py
   python kpi_analysis.py
   python visualization.py
   ```
6. Launch the interactive dashboard:
   ```
   streamlit run app.py
   ```

## Sample Charts

See `Output/Charts/` for all 15 generated chart images, including the
monthly revenue trend, category revenue share, and branch utilization
comparison.

## Author

Hitesh — B.Tech CSE, Lovely Professional University
