# Project Report: Vehicle Utilization & Rental Analytics

## 1. Business Problem

Our car rental business operates a fleet of 180 vehicles across 10 city
branches. Leadership needs to know: which vehicle categories and branches
actually drive profit once maintenance cost and downtime are accounted
for, which customer segments are worth investing marketing budget in, and
where operational issues (late returns, failed payments, maintenance
downtime) are quietly costing the business money.

## 2. Database Design

An 8-table, 3NF-normalised MySQL schema (`locations`, `vehicle_categories`,
`vehicles`, `customers`, `employees`, `rentals`, `payments`, `maintenance`)
stores the full transaction history. Full detail is in
`Documentation/er_diagram_notes.md`.

## 3. Methodology

Data was extracted from MySQL via `pandas.read_sql()`, cleaned (missing
values, duplicates, data types, text standardisation), validated for
logical consistency (no returns before pickup, no negative amounts), and
enriched with engineered features (rental duration, late-return flag, age
group, revenue per day). All 15 business questions were then answered
twice — once in SQL and once independently in Pandas — with matching
results, before being visualised and interpreted below.

## 4. Key Business Insights

### Insight 1 — SUVs are the clear revenue leader

- **Observation:** SUVs generate ₹1.60 crore in revenue (30.0% of total),
  ahead of Sedans (23.4%) and Luxury vehicles (21.3%), despite Luxury
  vehicles carrying the highest per-rental price.
- **Reason:** SUVs combine a high per-day rate with strong rental volume
  (1,348 rentals) — customers are willing to pay a premium for an SUV far
  more often than for a Luxury vehicle (452 rentals).
- **Business Impact:** The fleet is currently weighted toward Sedans and
  Hatchbacks by count, but revenue-per-vehicle economics favour SUVs —
  under-investing here leaves money on the table.
- **Recommendation:** Shift 5-10% of planned Sedan/Hatchback fleet
  expansion budget toward additional SUV units, starting in the highest-
  utilization branches (see Insight 4).

### Insight 2 — Late returns are a fleet-wide problem, worst in Luxury

- **Observation:** 18.1% of all completed rentals are returned late
  (2 of every 11 rentals), and the Luxury category has the highest rate
  at 19.5%, compared to 16.4% for Electric vehicles.
- **Reason:** Longer average rental durations (Luxury averages 3.96 days
  vs. the fleet's ~3.8-day average) give more opportunity for schedule
  slippage, and there is currently no visible penalty structure
  discouraging late returns.
- **Business Impact:** Late returns delay the next customer's pickup,
  increase cancellations, and erode fleet availability — effectively
  shrinking usable fleet-days without shrinking the fleet itself.
- **Recommendation:** Introduce a graduated late-return fee (with an
  automated SMS/email reminder 3 hours before the expected return time),
  piloted on the Luxury category first since it has the highest rate and
  the highest revenue-per-day at stake.

### Insight 3 — Regular and Silver members drive more total value than Platinum

- **Observation:** Regular members generate the most total revenue
  (₹2.26 crore from 367 customers), and Silver members have the highest
  average spend per customer (₹62,359) and highest rental frequency (6.24
  rentals/customer) — both ahead of Gold and Platinum.
- **Reason:** There are simply far more Regular and Silver customers (278
  and 367) than Platinum customers (74), and Silver-tier perks appear to
  be effectively encouraging repeat bookings.
- **Business Impact:** The premium membership tiers are not yet the
  primary revenue engine — the real opportunity is converting the large
  Regular base into Silver, where spend and frequency both step up.
- **Recommendation:** Focus loyalty-program marketing spend on a
  Regular-to-Silver upgrade campaign (e.g., "3 rentals to Silver") rather
  than on acquiring new Platinum sign-ups, which is a smaller and
  already-saturated segment.

### Insight 4 — Mumbai and Pune branches are most efficiently utilized

- **Observation:** Mumbai Andheri Branch leads fleet utilization at
  121.2 rented-days per vehicle, followed by Pune (119.5) and Hyderabad
  (119.3) — while Jaipur Central Hub trails at just 101.8 rented-days per
  vehicle.
- **Reason:** Mumbai and Pune combine large urban demand with efficient
  fleet sizing (23 and 18 vehicles respectively), while Jaipur's fleet may
  be oversized relative to local demand, or priced/marketed less
  effectively.
- **Business Impact:** Every rented-day of under-utilization at Jaipur is
  a vehicle sitting idle that could be earning revenue elsewhere — a ~16%
  utilization gap versus Mumbai on a 12-vehicle fleet is a meaningful lost
  opportunity.
- **Recommendation:** Reallocate 2-3 underused vehicles from Jaipur to
  Mumbai or Pune during peak months (October-January, May-June — see
  Insight 5), and review Jaipur's local pricing and promotional strategy.

### Insight 5 — Demand is strongly seasonal, peaking in Oct-Jan and May-Jun

- **Observation:** January (586 rentals, ₹62.2 lakh) and May (592 rentals,
  ₹57.9 lakh) are the strongest months, while July-September form a
  consistent trough (~310-320 rentals, ~₹31-32 lakh each).
- **Reason:** This lines up with holiday and wedding-season travel (Oct-
  Jan) and early-summer vacation travel (May-June), while the monsoon
  season (Jul-Sep) sees reduced road travel.
- **Business Impact:** Fleet and staffing that are sized for average
  demand will be short-staffed in peak months and over-staffed in the
  monsoon trough, costing either lost bookings or wasted labour cost.
- **Recommendation:** Build a seasonal staffing and short-term fleet-lease
  plan: scale up temporary fleet/staff capacity by ~15-20% from October
  through January and again in May-June, and use the July-September lull
  for scheduled maintenance (see Insight 6) to minimise revenue-day loss.

### Insight 6 — A small group of vehicles are barely profitable after maintenance cost

- **Observation:** The 10 least profitable vehicles (e.g., vehicle #103, a
  Tata Tiago) generated only ₹12,068-₹90,711 in net contribution after
  maintenance cost — some barely clearing their maintenance bill despite
  ₹82,000+ in gross rental revenue.
- **Reason:** These vehicles combine high maintenance spend (accident
  repairs and repeated servicing) with only moderate rental revenue,
  unlike top-performing vehicles of the same model.
- **Business Impact:** Continuing to operate these specific units ties up
  capital and branch space for a return far below the fleet average.
- **Recommendation:** Flag these 10 vehicle IDs for a retirement/resale
  review at their next scheduled service, and replace with new units of
  higher-performing categories (SUV/Sedan) identified in Insight 1.

## 5. Recommendations Summary

| # | Recommendation | Linked Insight |
|---|---|---|
| 1 | Shift fleet expansion budget toward SUVs | Insight 1 |
| 2 | Introduce a graduated late-fee + reminder system, starting with Luxury | Insight 2 |
| 3 | Run a Regular-to-Silver membership upgrade campaign | Insight 3 |
| 4 | Reallocate 2-3 vehicles from Jaipur to Mumbai/Pune | Insight 4 |
| 5 | Scale staffing/fleet ~15-20% for Oct-Jan and May-Jun; schedule maintenance in Jul-Sep | Insight 5 |
| 6 | Review the 10 lowest-net-contribution vehicles for retirement | Insight 6 |

## 6. Deliverables Checklist Status

See `Documentation/` and the handbook's Chapter 12 checklist — all SQL
phase deliverables (schema, sample data, views, stored procedure,
trigger, window functions) and Python phase deliverables (cleaning, EDA,
KPIs, charts, insights) are complete as of this report. Presentation
slides and a live/recorded demo remain to be prepared before submission.
