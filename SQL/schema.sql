-- =========================================================================
-- PROJECT: Vehicle Utilization & Rental Analytics
-- FILE:    schema.sql
-- PURPOSE: Creates the normalised (3NF) relational schema for the car
--          rental business. Run this first in MySQL Workbench / CLI.
-- =========================================================================

DROP DATABASE IF EXISTS car_rental_analytics;
CREATE DATABASE car_rental_analytics;
USE car_rental_analytics;

-- -------------------------------------------------------------------------
-- 1. LOCATIONS  (rental branches / pickup hubs)
-- -------------------------------------------------------------------------
CREATE TABLE locations (
    location_id     INT AUTO_INCREMENT PRIMARY KEY,
    location_name   VARCHAR(100) NOT NULL,
    city            VARCHAR(50)  NOT NULL,
    state           VARCHAR(50)  NOT NULL,
    region          VARCHAR(50)  NOT NULL
);

-- -------------------------------------------------------------------------
-- 2. VEHICLE_CATEGORIES (Economy, SUV, Luxury, Sedan, Hatchback, Van)
-- -------------------------------------------------------------------------
CREATE TABLE vehicle_categories (
    category_id     INT AUTO_INCREMENT PRIMARY KEY,
    category_name   VARCHAR(50) NOT NULL UNIQUE
);

-- -------------------------------------------------------------------------
-- 3. VEHICLES
-- -------------------------------------------------------------------------
CREATE TABLE vehicles (
    vehicle_id      INT AUTO_INCREMENT PRIMARY KEY,
    make            VARCHAR(50)  NOT NULL,
    model           VARCHAR(50)  NOT NULL,
    category_id     INT NOT NULL,
    manufacture_year INT NOT NULL CHECK (manufacture_year BETWEEN 2010 AND 2026),
    fuel_type       ENUM('Petrol','Diesel','Electric','Hybrid','CNG') NOT NULL,
    transmission    ENUM('Manual','Automatic') NOT NULL,
    seating_capacity INT NOT NULL,
    daily_rate      DECIMAL(10,2) NOT NULL CHECK (daily_rate > 0),
    odometer_km     INT NOT NULL DEFAULT 0,
    purchase_date   DATE NOT NULL,
    home_location_id INT NOT NULL,
    status          ENUM('Available','Rented','Under Maintenance','Retired') NOT NULL DEFAULT 'Available',
    CONSTRAINT fk_vehicle_category FOREIGN KEY (category_id) REFERENCES vehicle_categories(category_id),
    CONSTRAINT fk_vehicle_location FOREIGN KEY (home_location_id) REFERENCES locations(location_id)
);

-- -------------------------------------------------------------------------
-- 4. CUSTOMERS
-- -------------------------------------------------------------------------
CREATE TABLE customers (
    customer_id     INT AUTO_INCREMENT PRIMARY KEY,
    full_name       VARCHAR(100) NOT NULL,
    gender          ENUM('Male','Female','Other') NOT NULL,
    date_of_birth   DATE NOT NULL,
    city            VARCHAR(50) NOT NULL,
    membership_type ENUM('Regular','Silver','Gold','Platinum') NOT NULL DEFAULT 'Regular',
    join_date       DATE NOT NULL,
    CONSTRAINT chk_dob CHECK (date_of_birth < join_date)
);

-- -------------------------------------------------------------------------
-- 5. EMPLOYEES (branch staff who process pickups/returns)
-- -------------------------------------------------------------------------
CREATE TABLE employees (
    employee_id     INT AUTO_INCREMENT PRIMARY KEY,
    full_name       VARCHAR(100) NOT NULL,
    role            ENUM('Branch Manager','Rental Agent','Maintenance Staff') NOT NULL,
    location_id     INT NOT NULL,
    hire_date       DATE NOT NULL,
    CONSTRAINT fk_employee_location FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

-- -------------------------------------------------------------------------
-- 6. RENTALS (core fact/transaction table)
-- -------------------------------------------------------------------------
CREATE TABLE rentals (
    rental_id           INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id          INT NOT NULL,
    customer_id         INT NOT NULL,
    pickup_location_id  INT NOT NULL,
    return_location_id  INT NOT NULL,
    handled_by_employee INT NOT NULL,
    pickup_date         DATE NOT NULL,
    expected_return_date DATE NOT NULL,
    actual_return_date  DATE NULL,
    rental_status       ENUM('Completed','Ongoing','Cancelled') NOT NULL DEFAULT 'Completed',
    daily_rate_applied  DECIMAL(10,2) NOT NULL,
    total_amount        DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_rental_vehicle FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id),
    CONSTRAINT fk_rental_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT fk_rental_pickup_loc FOREIGN KEY (pickup_location_id) REFERENCES locations(location_id),
    CONSTRAINT fk_rental_return_loc FOREIGN KEY (return_location_id) REFERENCES locations(location_id),
    CONSTRAINT fk_rental_employee FOREIGN KEY (handled_by_employee) REFERENCES employees(employee_id),
    CONSTRAINT chk_return_after_pickup CHECK (expected_return_date >= pickup_date)
);

-- -------------------------------------------------------------------------
-- 7. PAYMENTS
-- -------------------------------------------------------------------------
CREATE TABLE payments (
    payment_id      INT AUTO_INCREMENT PRIMARY KEY,
    rental_id       INT NOT NULL,
    payment_date    DATE NOT NULL,
    amount          DECIMAL(10,2) NOT NULL CHECK (amount >= 0),
    payment_method  ENUM('Credit Card','Debit Card','UPI','Net Banking','Cash') NOT NULL,
    payment_status  ENUM('Success','Failed','Refunded','Pending') NOT NULL DEFAULT 'Success',
    CONSTRAINT fk_payment_rental FOREIGN KEY (rental_id) REFERENCES rentals(rental_id)
);

-- -------------------------------------------------------------------------
-- 8. MAINTENANCE
-- -------------------------------------------------------------------------
CREATE TABLE maintenance (
    maintenance_id   INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id       INT NOT NULL,
    maintenance_date DATE NOT NULL,
    maintenance_type ENUM('Routine Service','Repair','Accident Repair','Tire Change','Battery/Electric') NOT NULL,
    cost             DECIMAL(10,2) NOT NULL CHECK (cost >= 0),
    downtime_days    INT NOT NULL DEFAULT 1,
    CONSTRAINT fk_maintenance_vehicle FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
);

-- -------------------------------------------------------------------------
-- Helpful indexes for the analytics queries used later in the project
-- -------------------------------------------------------------------------
CREATE INDEX idx_rentals_vehicle   ON rentals(vehicle_id);
CREATE INDEX idx_rentals_customer  ON rentals(customer_id);
CREATE INDEX idx_rentals_pickup    ON rentals(pickup_date);
CREATE INDEX idx_payments_rental   ON payments(rental_id);
CREATE INDEX idx_maintenance_veh   ON maintenance(vehicle_id);
