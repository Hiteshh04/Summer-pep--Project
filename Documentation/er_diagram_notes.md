# Entity-Relationship Reference — Vehicle Utilization & Rental Analytics

This document describes the schema defined in `SQL/schema.sql`. Export a
visual ER diagram from MySQL Workbench (Database → Reverse Engineer, after
running schema.sql) and save it here as `er_diagram.png` for your report
and README, per Handbook Chapter 9/10.

## Entities & Key Attributes

| Entity | Primary Key | Description |
|---|---|---|
| `locations` | location_id | Rental branches / pickup hubs |
| `vehicle_categories` | category_id | Hatchback, Sedan, SUV, Luxury, Van, Electric |
| `vehicles` | vehicle_id | Fleet inventory: make, model, rate, status |
| `customers` | customer_id | Renter details incl. membership tier |
| `employees` | employee_id | Branch staff who process rentals |
| `rentals` | rental_id | Core transaction: one row per booking |
| `payments` | payment_id | One or more payments per rental |
| `maintenance` | maintenance_id | Service/repair history per vehicle |

## Relationships (Foreign Keys)

- `vehicles.category_id` → `vehicle_categories.category_id` (many-to-one)
- `vehicles.home_location_id` → `locations.location_id` (many-to-one)
- `employees.location_id` → `locations.location_id` (many-to-one)
- `rentals.vehicle_id` → `vehicles.vehicle_id` (many-to-one)
- `rentals.customer_id` → `customers.customer_id` (many-to-one)
- `rentals.pickup_location_id` / `return_location_id` → `locations.location_id`
  (two separate foreign keys — supports one-way branch drop-offs)
- `rentals.handled_by_employee` → `employees.employee_id` (many-to-one)
- `payments.rental_id` → `rentals.rental_id` (one rental can have several
  payment attempts/refunds)
- `maintenance.vehicle_id` → `vehicles.vehicle_id` (many-to-one)

## Normalisation Notes (3NF)

- Every non-key attribute depends only on its table's primary key (no
  partial dependencies — e.g. `category_name` lives only in
  `vehicle_categories`, not repeated on every vehicle row).
- No transitive dependencies: `rentals` stores `daily_rate_applied` at
  the time of booking (a business requirement, since a vehicle's
  `daily_rate` can change later) rather than deriving it awkwardly, and
  this is explicitly documented as an intentional denormalisation for
  historical accuracy — not a normalisation gap.
- Repeating groups are eliminated: a customer can have unlimited rentals
  without any repeated columns, because `rentals` is its own table
  linked by foreign key rather than columns like `rental_1`, `rental_2`.
