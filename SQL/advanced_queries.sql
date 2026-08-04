-- =========================================================================
-- PROJECT: Vehicle Utilization & Rental Analytics
-- FILE:    advanced_queries.sql
-- PURPOSE: 15 business case studies (with solved SQL), plus Views,
--          a Stored Procedure, a Trigger, and Window Function examples,
--          as required by the SQL Phase deliverables checklist.
-- RUN AFTER: schema.sql and sample_data.sql
-- =========================================================================
USE car_rental_analytics;


-- #########################################################################
-- SECTION A: 15 BUSINESS CASE STUDIES
-- #########################################################################

-- -------------------------------------------------------------------------
-- CASE STUDY 1
-- Business Question: What is the month-over-month revenue trend, and
-- which months are our strongest and weakest for the business?
-- -------------------------------------------------------------------------
SELECT
    DATE_FORMAT(pickup_date, '%Y-%m') AS rental_month,
    COUNT(*)                          AS total_rentals,
    ROUND(SUM(total_amount), 2)       AS total_revenue,
    ROUND(AVG(total_amount), 2)       AS avg_rental_value
FROM rentals
WHERE rental_status = 'Completed'
GROUP BY rental_month
ORDER BY rental_month;


-- -------------------------------------------------------------------------
-- CASE STUDY 2
-- Business Question: Which vehicle category generates the most revenue,
-- and how many rentals and what average duration does each category see?
-- -------------------------------------------------------------------------
SELECT
    vc.category_name,
    COUNT(r.rental_id)                                   AS total_rentals,
    ROUND(SUM(r.total_amount), 2)                         AS total_revenue,
    ROUND(AVG(DATEDIFF(r.actual_return_date, r.pickup_date)), 2) AS avg_duration_days
FROM rentals r
JOIN vehicles v            ON r.vehicle_id = v.vehicle_id
JOIN vehicle_categories vc ON v.category_id = vc.category_id
WHERE r.rental_status = 'Completed'
GROUP BY vc.category_name
ORDER BY total_revenue DESC;


-- -------------------------------------------------------------------------
-- CASE STUDY 3
-- Business Question: Which are our top 10 most-rented vehicles, and how
-- much revenue does each contribute?
-- -------------------------------------------------------------------------
SELECT
    v.vehicle_id, v.make, v.model, vc.category_name,
    COUNT(r.rental_id)            AS times_rented,
    ROUND(SUM(r.total_amount), 2) AS revenue_generated
FROM rentals r
JOIN vehicles v            ON r.vehicle_id = v.vehicle_id
JOIN vehicle_categories vc ON v.category_id = vc.category_id
WHERE r.rental_status = 'Completed'
GROUP BY v.vehicle_id, v.make, v.model, vc.category_name
ORDER BY times_rented DESC
LIMIT 10;


-- -------------------------------------------------------------------------
-- CASE STUDY 4
-- Business Question: Which branch (location) generates the highest
-- revenue, and which has the highest average rental value?
-- -------------------------------------------------------------------------
SELECT
    l.location_name, l.city,
    COUNT(r.rental_id)             AS total_rentals,
    ROUND(SUM(r.total_amount), 2)  AS total_revenue,
    ROUND(AVG(r.total_amount), 2)  AS avg_rental_value
FROM rentals r
JOIN locations l ON r.pickup_location_id = l.location_id
WHERE r.rental_status = 'Completed'
GROUP BY l.location_name, l.city
ORDER BY total_revenue DESC;


-- -------------------------------------------------------------------------
-- CASE STUDY 5
-- Business Question: How do our four membership tiers differ in rental
-- frequency and average spend per customer?
-- -------------------------------------------------------------------------
SELECT
    c.membership_type,
    COUNT(DISTINCT c.customer_id)                       AS customers,
    COUNT(r.rental_id)                                  AS total_rentals,
    ROUND(COUNT(r.rental_id) / COUNT(DISTINCT c.customer_id), 2) AS rentals_per_customer,
    ROUND(SUM(r.total_amount), 2)                       AS total_revenue,
    ROUND(SUM(r.total_amount) / COUNT(DISTINCT c.customer_id), 2) AS avg_spend_per_customer
FROM customers c
JOIN rentals r ON c.customer_id = r.customer_id
WHERE r.rental_status = 'Completed'
GROUP BY c.membership_type
ORDER BY avg_spend_per_customer DESC;


-- -------------------------------------------------------------------------
-- CASE STUDY 6
-- Business Question: What is the average rental duration per category,
-- and does longer duration correlate with higher total revenue share?
-- (See Case Study 2 for the duration figures; this view expresses revenue
--  share explicitly using a window function.)
-- -------------------------------------------------------------------------
SELECT
    vc.category_name,
    ROUND(SUM(r.total_amount), 2) AS category_revenue,
    ROUND(100 * SUM(r.total_amount) / SUM(SUM(r.total_amount)) OVER (), 2) AS pct_of_total_revenue
FROM rentals r
JOIN vehicles v            ON r.vehicle_id = v.vehicle_id
JOIN vehicle_categories vc ON v.category_id = vc.category_id
WHERE r.rental_status = 'Completed'
GROUP BY vc.category_name
ORDER BY category_revenue DESC;


-- -------------------------------------------------------------------------
-- CASE STUDY 7
-- Business Question: What percentage of rentals are returned late, and
-- which vehicle category has the worst late-return rate?
-- -------------------------------------------------------------------------
SELECT
    vc.category_name,
    COUNT(*) AS total_completed,
    SUM(CASE WHEN r.actual_return_date > r.expected_return_date THEN 1 ELSE 0 END) AS late_returns,
    ROUND(100 * SUM(CASE WHEN r.actual_return_date > r.expected_return_date THEN 1 ELSE 0 END)
          / COUNT(*), 2) AS late_return_pct
FROM rentals r
JOIN vehicles v            ON r.vehicle_id = v.vehicle_id
JOIN vehicle_categories vc ON v.category_id = vc.category_id
WHERE r.rental_status = 'Completed'
GROUP BY vc.category_name
ORDER BY late_return_pct DESC;


-- -------------------------------------------------------------------------
-- CASE STUDY 8
-- Business Question: How much does maintenance cost eat into each
-- vehicle's rental revenue? Which vehicles are the least profitable
-- once maintenance cost is accounted for?
-- -------------------------------------------------------------------------
SELECT
    v.vehicle_id, v.make, v.model,
    COALESCE(rev.total_revenue, 0)  AS rental_revenue,
    COALESCE(m.total_maint_cost, 0) AS maintenance_cost,
    COALESCE(rev.total_revenue, 0) - COALESCE(m.total_maint_cost, 0) AS net_contribution
FROM vehicles v
LEFT JOIN (
    SELECT vehicle_id, SUM(total_amount) AS total_revenue
    FROM rentals WHERE rental_status = 'Completed'
    GROUP BY vehicle_id
) rev ON v.vehicle_id = rev.vehicle_id
LEFT JOIN (
    SELECT vehicle_id, SUM(cost) AS total_maint_cost
    FROM maintenance
    GROUP BY vehicle_id
) m ON v.vehicle_id = m.vehicle_id
ORDER BY net_contribution ASC
LIMIT 10;


-- -------------------------------------------------------------------------
-- CASE STUDY 9
-- Business Question: Which months show peak seasonal demand, so we can
-- plan fleet allocation and pricing ahead of time?
-- -------------------------------------------------------------------------
SELECT
    MONTHNAME(pickup_date) AS month_name,
    MONTH(pickup_date)     AS month_num,
    COUNT(*)               AS total_rentals,
    ROUND(SUM(total_amount), 2) AS total_revenue
FROM rentals
WHERE rental_status = 'Completed'
GROUP BY month_name, month_num
ORDER BY month_num;


-- -------------------------------------------------------------------------
-- CASE STUDY 10
-- Business Question: Which fuel type do customers rent most, and which
-- fuel type earns the highest revenue per rental?
-- -------------------------------------------------------------------------
SELECT
    v.fuel_type,
    COUNT(r.rental_id)             AS total_rentals,
    ROUND(SUM(r.total_amount), 2)  AS total_revenue,
    ROUND(AVG(r.total_amount), 2)  AS avg_revenue_per_rental
FROM rentals r
JOIN vehicles v ON r.vehicle_id = v.vehicle_id
WHERE r.rental_status = 'Completed'
GROUP BY v.fuel_type
ORDER BY total_revenue DESC;


-- -------------------------------------------------------------------------
-- CASE STUDY 11
-- Business Question: Which age group of customers prefers which vehicle
-- category, so marketing can target the right segment?
-- -------------------------------------------------------------------------
SELECT
    CASE
        WHEN TIMESTAMPDIFF(YEAR, c.date_of_birth, CURDATE()) BETWEEN 21 AND 30 THEN '21-30'
        WHEN TIMESTAMPDIFF(YEAR, c.date_of_birth, CURDATE()) BETWEEN 31 AND 45 THEN '31-45'
        WHEN TIMESTAMPDIFF(YEAR, c.date_of_birth, CURDATE()) BETWEEN 46 AND 60 THEN '46-60'
        ELSE '60+'
    END AS age_group,
    vc.category_name,
    COUNT(*) AS total_rentals
FROM rentals r
JOIN customers c           ON r.customer_id = c.customer_id
JOIN vehicles v             ON r.vehicle_id = v.vehicle_id
JOIN vehicle_categories vc  ON v.category_id = vc.category_id
WHERE r.rental_status = 'Completed'
GROUP BY age_group, vc.category_name
ORDER BY age_group, total_rentals DESC;


-- -------------------------------------------------------------------------
-- CASE STUDY 12
-- Business Question: What does our payment method mix look like, and
-- what is the failed-payment rate we need to reduce?
-- -------------------------------------------------------------------------
SELECT
    payment_method,
    COUNT(*)                                          AS total_payments,
    SUM(CASE WHEN payment_status = 'Failed' THEN 1 ELSE 0 END) AS failed_payments,
    ROUND(100 * SUM(CASE WHEN payment_status = 'Failed' THEN 1 ELSE 0 END) / COUNT(*), 2) AS failed_pct,
    ROUND(SUM(CASE WHEN payment_status = 'Success' THEN amount ELSE 0 END), 2) AS revenue_collected
FROM payments
GROUP BY payment_method
ORDER BY total_payments DESC;


-- -------------------------------------------------------------------------
-- CASE STUDY 13
-- Business Question: Which vehicles have lost the most days to
-- maintenance downtime, reducing their availability to rent?
-- -------------------------------------------------------------------------
SELECT
    v.vehicle_id, v.make, v.model, vc.category_name,
    COUNT(m.maintenance_id)        AS maintenance_events,
    SUM(m.downtime_days)           AS total_downtime_days,
    ROUND(SUM(m.cost), 2)          AS total_maintenance_cost
FROM maintenance m
JOIN vehicles v            ON m.vehicle_id = v.vehicle_id
JOIN vehicle_categories vc ON v.category_id = vc.category_id
GROUP BY v.vehicle_id, v.make, v.model, vc.category_name
ORDER BY total_downtime_days DESC
LIMIT 10;


-- -------------------------------------------------------------------------
-- CASE STUDY 14
-- Business Question: Who are our top 10 highest lifetime-value
-- customers, ranked using a window function?
-- -------------------------------------------------------------------------
SELECT customer_id, full_name, membership_type, total_spend, customer_rank
FROM (
    SELECT
        c.customer_id, c.full_name, c.membership_type,
        SUM(r.total_amount) AS total_spend,
        RANK() OVER (ORDER BY SUM(r.total_amount) DESC) AS customer_rank
    FROM rentals r
    JOIN customers c ON r.customer_id = c.customer_id
    WHERE r.rental_status = 'Completed'
    GROUP BY c.customer_id, c.full_name, c.membership_type
) ranked
WHERE customer_rank <= 10;


-- -------------------------------------------------------------------------
-- CASE STUDY 15
-- Business Question: What is each branch's vehicle utilization rate
-- (share of fleet-days actually rented), so we can spot under- or
-- over-utilized branches?
-- -------------------------------------------------------------------------
SELECT
    l.location_name, l.city,
    COUNT(DISTINCT v.vehicle_id)                    AS fleet_size,
    COUNT(r.rental_id)                              AS total_rentals,
    ROUND(SUM(DATEDIFF(r.actual_return_date, r.pickup_date)), 0) AS total_rented_days,
    ROUND(SUM(DATEDIFF(r.actual_return_date, r.pickup_date))
          / COUNT(DISTINCT v.vehicle_id), 2)        AS rented_days_per_vehicle
FROM locations l
JOIN vehicles v ON v.home_location_id = l.location_id
LEFT JOIN rentals r ON r.vehicle_id = v.vehicle_id AND r.rental_status = 'Completed'
GROUP BY l.location_name, l.city
ORDER BY rented_days_per_vehicle DESC;


-- #########################################################################
-- SECTION B: VIEWS
-- #########################################################################

-- View 1: A ready-to-query view of completed rentals with all dimension
-- fields joined in. Python's read_sql() can query this view directly
-- instead of repeating the joins in every script.
CREATE OR REPLACE VIEW vw_completed_rentals AS
SELECT
    r.rental_id, r.pickup_date, r.expected_return_date, r.actual_return_date,
    DATEDIFF(r.actual_return_date, r.pickup_date) AS rental_days,
    r.total_amount,
    v.vehicle_id, v.make, v.model, v.fuel_type, v.transmission,
    vc.category_name,
    c.customer_id, c.full_name AS customer_name, c.membership_type, c.gender,
    pl.location_name AS pickup_location, pl.city AS pickup_city,
    rl.location_name AS return_location
FROM rentals r
JOIN vehicles v            ON r.vehicle_id = v.vehicle_id
JOIN vehicle_categories vc  ON v.category_id = vc.category_id
JOIN customers c            ON r.customer_id = c.customer_id
JOIN locations pl           ON r.pickup_location_id = pl.location_id
JOIN locations rl           ON r.return_location_id = rl.location_id
WHERE r.rental_status = 'Completed';

-- View 2: Monthly revenue summary, reused by the KPI/reporting scripts.
CREATE OR REPLACE VIEW vw_monthly_revenue AS
SELECT
    DATE_FORMAT(pickup_date, '%Y-%m') AS rental_month,
    COUNT(*)                          AS total_rentals,
    ROUND(SUM(total_amount), 2)       AS total_revenue
FROM rentals
WHERE rental_status = 'Completed'
GROUP BY rental_month;


-- #########################################################################
-- SECTION C: STORED PROCEDURE
-- #########################################################################

DELIMITER //

-- Returns a revenue + rental-count summary for any date range, so the
-- Python phase (or a manager) can call one procedure instead of writing
-- a fresh query every time.
CREATE PROCEDURE sp_revenue_by_period(IN p_start_date DATE, IN p_end_date DATE)
BEGIN
    SELECT
        COUNT(*)                       AS total_rentals,
        ROUND(SUM(total_amount), 2)    AS total_revenue,
        ROUND(AVG(total_amount), 2)    AS avg_rental_value
    FROM rentals
    WHERE rental_status = 'Completed'
      AND pickup_date BETWEEN p_start_date AND p_end_date;
END //

DELIMITER ;

-- Example call:
-- CALL sp_revenue_by_period('2025-01-01', '2025-12-31');


-- #########################################################################
-- SECTION D: TRIGGER
-- #########################################################################

DELIMITER //

-- Whenever a new rental is inserted as 'Ongoing', automatically flip the
-- vehicle's status to 'Rented' so the fleet table always reflects reality
-- without a separate manual update step.
CREATE TRIGGER trg_set_vehicle_rented
AFTER INSERT ON rentals
FOR EACH ROW
BEGIN
    IF NEW.rental_status = 'Ongoing' THEN
        UPDATE vehicles SET status = 'Rented' WHERE vehicle_id = NEW.vehicle_id;
    END IF;
END //

DELIMITER ;


-- #########################################################################
-- SECTION E: EXTRA WINDOW-FUNCTION EXAMPLES
-- #########################################################################

-- Running (cumulative) monthly revenue total across the whole business.
SELECT
    rental_month, total_revenue,
    SUM(total_revenue) OVER (ORDER BY rental_month) AS cumulative_revenue
FROM vw_monthly_revenue
ORDER BY rental_month;

-- Rank vehicles by revenue WITHIN their own category (ROW_NUMBER, partitioned).
SELECT * FROM (
    SELECT
        vc.category_name, v.vehicle_id, v.make, v.model,
        SUM(r.total_amount) AS vehicle_revenue,
        ROW_NUMBER() OVER (PARTITION BY vc.category_name ORDER BY SUM(r.total_amount) DESC) AS rank_in_category
    FROM rentals r
    JOIN vehicles v            ON r.vehicle_id = v.vehicle_id
    JOIN vehicle_categories vc ON v.category_id = vc.category_id
    WHERE r.rental_status = 'Completed'
    GROUP BY vc.category_name, v.vehicle_id, v.make, v.model
) ranked
WHERE rank_in_category <= 3
ORDER BY category_name, rank_in_category;
