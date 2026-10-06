"""Synthetic phase-four data for designed-species and interplanetary scenarios (2028-2030).

This dataset introduces:
- Designer-created species (poodle-unicorns, yeti-narwhals, etc.)
- One-to-many print attempts and failed production costs
- Habitat requirements with versioned rules
- Planets, universes, and shipping routes
- Effective-dated rates and conversion rules
- Quote vs. actual shipping cost variance
- Temporal joins and operational recovery scenarios

Scenario progression:
- 2028: Print jobs, design versions, failed attempts, costs
- 2029: Alien species, universes, currencies, measurement units
- 2030: Multi-leg shipments, habitat capacity, outages, returns
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

DESIGNERS = [
    ("designer_001", "Luna Craft Studios", "Denver", "2028-01-01"),
    ("designer_002", "Cosmic Paws Lab", "Boulder", "2028-01-15"),
    ("designer_003", "Hybrid Haven", "Fort Collins", "2028-02-01"),
]

DESIGNED_SPECIES = [
    {
        "species_id": "species_designed_001",
        "designer_id": "designer_001",
        "design_name": "Poodle-Unicorn",
        "parent_species_1": "Dog",
        "parent_species_2": "Mythical Equine",
        "design_version": "2028-poodle-unicorn-v1",
        "created_date": "2028-01-10",
        "rule_version": "2028-01-design-v1",
    },
    {
        "species_id": "species_designed_002",
        "designer_id": "designer_002",
        "design_name": "Yeti-Narwhal",
        "parent_species_1": "Yeti",
        "parent_species_2": "Narwhal",
        "design_version": "2028-yeti-narwhal-v1",
        "created_date": "2028-01-20",
        "rule_version": "2028-01-design-v1",
    },
    {
        "species_id": "species_designed_003",
        "designer_id": "designer_003",
        "design_name": "Phoenix-Dragon",
        "parent_species_1": "Phoenix",
        "parent_species_2": "Dragon",
        "design_version": "2028-phoenix-dragon-v1",
        "created_date": "2028-02-05",
        "rule_version": "2028-01-design-v1",
    },
]

PRINT_JOBS = [
    {
        "job_id": "job_001",
        "species_id": "species_designed_001",
        "design_version": "2028-poodle-unicorn-v1",
        "ordered_date": "2028-02-01",
        "ordered_quantity": 3,
        "completed_quantity": 2,
    },
    {
        "job_id": "job_002",
        "species_id": "species_designed_002",
        "design_version": "2028-yeti-narwhal-v1",
        "ordered_date": "2028-02-15",
        "ordered_quantity": 2,
        "completed_quantity": 1,
    },
    {
        "job_id": "job_003",
        "species_id": "species_designed_003",
        "design_version": "2028-phoenix-dragon-v1",
        "ordered_date": "2028-03-01",
        "ordered_quantity": 4,
        "completed_quantity": 3,
    },
]

PRINT_ATTEMPTS = [
    ("attempt_001", "job_001", 1, "2028-02-05", "2028-02-08", "success", 50.00, 0.00, None),
    ("attempt_002", "job_001", 2, "2028-02-09", "2028-02-12", "success", 50.00, 0.00, None),
    ("attempt_003", "job_001", 3, "2028-02-13", "2028-02-19", "failed", 0.00, 50.00, "material_degradation"),
    ("attempt_004", "job_002", 1, "2028-02-20", "2028-02-25", "success", 75.00, 0.00, None),
    ("attempt_005", "job_002", 2, "2028-02-26", "2028-03-03", "failed", 0.00, 75.00, "power_outage"),
    ("attempt_006", "job_003", 1, "2028-03-05", "2028-03-10", "success", 60.00, 0.00, None),
    ("attempt_007", "job_003", 2, "2028-03-11", "2028-03-15", "success", 60.00, 0.00, None),
    ("attempt_008", "job_003", 3, "2028-03-16", "2028-03-20", "success", 60.00, 0.00, None),
    ("attempt_009", "job_003", 4, "2028-03-21", "2028-03-28", "failed", 0.00, 60.00, "design_mismatch"),
]

PRINTED_CREATURES = [
    ("creature_printed_001", "attempt_001", "species_designed_001", "agency_001", "Poodle-Uni-A", "2028-02-08", "Available"),
    ("creature_printed_002", "attempt_002", "species_designed_001", "agency_002", "Poodle-Uni-B", "2028-02-12", "Available"),
    ("creature_printed_003", "attempt_004", "species_designed_002", "agency_005", "Yeti-Narwhal-One", "2028-02-25", "Pending"),
    ("creature_printed_004", "attempt_006", "species_designed_003", "agency_008", "Phoenix-Dragon-Alpha", "2028-03-10", "Available"),
    ("creature_printed_005", "attempt_007", "species_designed_003", "agency_010", "Phoenix-Dragon-Beta", "2028-03-15", "Available"),
    ("creature_printed_006", "attempt_008", "species_designed_003", "agency_012", "Phoenix-Dragon-Gamma", "2028-03-20", "Available"),
]

UNIVERSES = [
    ("universe_0", "Earth", 0, "home_universe", None),
    ("universe_1", "Promeathea", 1, "fictional_alien", None),
    ("universe_2", "Kepler-442b System", 2, "fictional_alien", None),
    ("universe_3", "Tau Ceti Realm", 3, "fictional_alien", None),
]

PLANETS = [
    ("planet_earth", "universe_0", "Earth", "planet", "Sol System", 1.0, "standard"),
    ("planet_promeathea_prime", "universe_1", "Promeathea Prime", "planet", "Promeathea System", 0.8, "high_gravity"),
    ("planet_kepler_442b", "universe_2", "Kepler-442b", "planet", "Kepler-442b System", 1.3, "variable_atmosphere"),
    ("planet_tau_ceti_alpha", "universe_3", "Tau Ceti Alpha", "planet", "Tau Ceti System", 0.9, "exotic_conditions"),
]

HABITAT_REQUIREMENTS = [
    {
        "requirement_id": "habitat_req_001",
        "species_id": "species_designed_001",
        "temp_min_celsius": 15.0,
        "temp_max_celsius": 25.0,
        "pressure_kpa": 101.325,
        "atmosphere": "nitrogen-oxygen",
        "gravity_g": 1.0,
        "water_chemistry": "fresh",
        "effective_from": "2028-01-10",
        "effective_to": None,
        "rule_version": "2028-01-design-v1",
    },
    {
        "requirement_id": "habitat_req_002",
        "species_id": "species_designed_002",
        "temp_min_celsius": -10.0,
        "temp_max_celsius": 5.0,
        "pressure_kpa": 90.0,
        "atmosphere": "nitrogen-oxygen-argon",
        "gravity_g": 0.8,
        "water_chemistry": "salt",
        "effective_from": "2028-01-20",
        "effective_to": None,
        "rule_version": "2028-01-design-v1",
    },
    {
        "requirement_id": "habitat_req_003",
        "species_id": "species_designed_003",
        "temp_min_celsius": 20.0,
        "temp_max_celsius": 35.0,
        "pressure_kpa": 110.0,
        "atmosphere": "nitrogen-oxygen",
        "gravity_g": 1.2,
        "water_chemistry": "mineral",
        "effective_from": "2028-02-05",
        "effective_to": None,
        "rule_version": "2028-01-design-v1",
    },
]

HABITAT_CAPACITY = [
    ("capacity_001", "planet_earth", 100, 45, "2028-01-01", None),
    ("capacity_002", "planet_promeathea_prime", 50, 12, "2028-06-01", None),
    ("capacity_003", "planet_kepler_442b", 75, 30, "2028-07-01", None),
    ("capacity_004", "planet_tau_ceti_alpha", 30, 5, "2028-08-01", None),
]

SHIPPING_ROUTES = [
    ("route_001", "planet_earth", "planet_promeathea_prime", "jump_gate", 1, 14.0, "2028-06-01", None),
    ("route_002", "planet_earth", "planet_kepler_442b", "jump_gate", 1, 21.0, "2028-07-01", None),
    ("route_003", "planet_earth", "planet_tau_ceti_alpha", "jump_gate", 2, 35.0, "2028-08-01", None),
    ("route_004", "planet_promeathea_prime", "planet_kepler_442b", "direct", 1, 10.5, "2028-07-15", None),
]

EXCHANGE_RATES = [
    ("rate_001", "USD", "Promeathean Credits", 1.0, 2.5, "2028-06-01", "2028-12-31"),
    ("rate_002", "USD", "Kepler Marks", 1.0, 3.2, "2028-07-01", "2028-12-31"),
    ("rate_003", "USD", "Tau Ceti Numerals", 1.0, 4.1, "2028-08-01", "2028-12-31"),
]

SHIPPING_QUOTES = [
    {
        "quote_id": "quote_001",
        "creature_id": "creature_printed_001",
        "destination_planet": "planet_promeathea_prime",
        "route_id": "route_001",
        "quote_date": "2028-06-15",
        "quote_expiry": "2028-07-15",
        "base_charge_usd": 500.0,
        "mass_volume_charge_usd": 150.0,
        "containment_charge_usd": 100.0,
        "life_support_charge_usd": 200.0,
        "customs_charge_usd": 50.0,
        "total_quoted_usd": 1000.0,
        "currency": "USD",
        "rate_version": "2028-06-rates-v1",
        "status": "accepted",
    },
    {
        "quote_id": "quote_002",
        "creature_id": "creature_printed_003",
        "destination_planet": "planet_kepler_442b",
        "route_id": "route_002",
        "quote_date": "2028-07-10",
        "quote_expiry": "2028-08-10",
        "base_charge_usd": 700.0,
        "mass_volume_charge_usd": 250.0,
        "containment_charge_usd": 150.0,
        "life_support_charge_usd": 300.0,
        "customs_charge_usd": 75.0,
        "total_quoted_usd": 1475.0,
        "currency": "USD",
        "rate_version": "2028-07-rates-v1",
        "status": "pending_habitat_check",
    },
    {
        "quote_id": "quote_003",
        "creature_id": "creature_printed_004",
        "destination_planet": "planet_promeathea_prime",
        "route_id": "route_001",
        "quote_date": "2028-07-01",
        "quote_expiry": "2028-08-01",
        "base_charge_usd": 550.0,
        "mass_volume_charge_usd": 180.0,
        "containment_charge_usd": 120.0,
        "life_support_charge_usd": 220.0,
        "customs_charge_usd": 55.0,
        "total_quoted_usd": 1125.0,
        "currency": "USD",
        "rate_version": "2028-07-rates-v1",
        "status": "accepted",
    },
]

SHIPMENT_LEGS = [
    ("leg_001", "quote_001", 1, "planet_earth", "planet_promeathea_prime", "2028-07-01", "2028-07-15", "completed"),
    ("leg_002", "quote_003", 1, "planet_earth", "planet_promeathea_prime", "2028-07-05", "2028-07-19", "completed"),
]

SHIPMENT_EVENTS = [
    ("event_leg_001", "leg_001", "departed", "2028-07-01", 1, None),
    ("event_leg_002", "leg_001", "in_transit", "2028-07-08", 2, None),
    ("event_leg_003", "leg_001", "arrived", "2028-07-15", 3, None),
    ("event_leg_004", "leg_002", "departed", "2028-07-05", 1, None),
    ("event_leg_005", "leg_002", "in_transit", "2028-07-12", 2, None),
    ("event_leg_006", "leg_002", "arrived", "2028-07-19", 3, None),
]

ACTUAL_SHIPPING_COSTS = [
    ("cost_001", "leg_001", "base", 500.0, "USD", "2028-07-15", "quote_001"),
    ("cost_002", "leg_001", "mass_volume", 160.0, "USD", "2028-07-15", "quote_001"),
    ("cost_003", "leg_001", "containment", 100.0, "USD", "2028-07-15", "quote_001"),
    ("cost_004", "leg_001", "life_support", 210.0, "USD", "2028-07-15", "quote_001"),
    ("cost_005", "leg_001", "customs", 50.0, "USD", "2028-07-15", "quote_001"),
    ("cost_006", "leg_002", "base", 550.0, "USD", "2028-07-19", "quote_003"),
    ("cost_007", "leg_002", "mass_volume", 185.0, "USD", "2028-07-19", "quote_003"),
    ("cost_008", "leg_002", "containment", 120.0, "USD", "2028-07-19", "quote_003"),
    ("cost_009", "leg_002", "life_support", 225.0, "USD", "2028-07-19", "quote_003"),
    ("cost_010", "leg_002", "customs", 55.0, "USD", "2028-07-19", "quote_003"),
]


def create_phase_four_database(connection: sqlite3.Connection) -> None:
    """Create a deterministic designed-species and interplanetary dataset.

    Demonstrates:
    - Print job tracking with failed-attempt costs
    - Design versions and lineage
    - Habitat requirements with effective-dated rules
    - Multi-universe geography and shipping routes
    - Quoted vs. actual shipping cost reconciliation
    - Exchange rates and currency normalization
    """
    connection.executescript(
        """
        CREATE TABLE designers (
            designer_id TEXT PRIMARY KEY,
            designer_name TEXT NOT NULL,
            location TEXT NOT NULL,
            created_date TEXT NOT NULL
        );

        CREATE TABLE designed_species (
            species_id TEXT PRIMARY KEY,
            designer_id TEXT NOT NULL,
            design_name TEXT NOT NULL,
            parent_species_1 TEXT,
            parent_species_2 TEXT,
            design_version TEXT NOT NULL,
            created_date TEXT NOT NULL,
            rule_version TEXT NOT NULL,
            FOREIGN KEY (designer_id) REFERENCES designers(designer_id)
        );

        CREATE TABLE print_jobs (
            job_id TEXT PRIMARY KEY,
            species_id TEXT NOT NULL,
            design_version TEXT NOT NULL,
            ordered_date TEXT NOT NULL,
            ordered_quantity INTEGER NOT NULL,
            completed_quantity INTEGER NOT NULL,
            FOREIGN KEY (species_id) REFERENCES designed_species(species_id)
        );

        CREATE TABLE print_attempts (
            attempt_id TEXT PRIMARY KEY,
            job_id TEXT NOT NULL,
            attempt_number INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            outcome TEXT NOT NULL,
            labor_cost_usd REAL NOT NULL,
            failed_cost_usd REAL NOT NULL,
            failure_reason TEXT,
            FOREIGN KEY (job_id) REFERENCES print_jobs(job_id)
        );

        CREATE TABLE printed_creatures (
            creature_id TEXT PRIMARY KEY,
            attempt_id TEXT NOT NULL,
            species_id TEXT NOT NULL,
            agency_id TEXT NOT NULL,
            name TEXT NOT NULL,
            created_date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (attempt_id) REFERENCES print_attempts(attempt_id),
            FOREIGN KEY (species_id) REFERENCES designed_species(species_id)
        );

        CREATE TABLE universes (
            universe_id TEXT PRIMARY KEY,
            universe_name TEXT NOT NULL,
            universe_number INTEGER NOT NULL,
            universe_type TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE planets (
            planet_id TEXT PRIMARY KEY,
            universe_id TEXT NOT NULL,
            planet_name TEXT NOT NULL,
            location_type TEXT NOT NULL,
            system_name TEXT NOT NULL,
            gravity_multiplier REAL NOT NULL,
            atmosphere_type TEXT NOT NULL,
            FOREIGN KEY (universe_id) REFERENCES universes(universe_id)
        );

        CREATE TABLE habitat_requirements (
            requirement_id TEXT PRIMARY KEY,
            species_id TEXT NOT NULL,
            temp_min_celsius REAL NOT NULL,
            temp_max_celsius REAL NOT NULL,
            pressure_kpa REAL NOT NULL,
            atmosphere TEXT NOT NULL,
            gravity_g REAL NOT NULL,
            water_chemistry TEXT NOT NULL,
            effective_from TEXT NOT NULL,
            effective_to TEXT,
            rule_version TEXT NOT NULL,
            FOREIGN KEY (species_id) REFERENCES designed_species(species_id)
        );

        CREATE TABLE habitat_capacity (
            capacity_id TEXT PRIMARY KEY,
            planet_id TEXT NOT NULL,
            total_capacity INTEGER NOT NULL,
            reserved_capacity INTEGER NOT NULL,
            observation_date TEXT NOT NULL,
            version_date TEXT,
            FOREIGN KEY (planet_id) REFERENCES planets(planet_id)
        );

        CREATE TABLE shipping_routes (
            route_id TEXT PRIMARY KEY,
            origin_planet TEXT NOT NULL,
            destination_planet TEXT NOT NULL,
            transport_method TEXT NOT NULL,
            leg_count INTEGER NOT NULL,
            transit_days REAL NOT NULL,
            effective_from TEXT NOT NULL,
            effective_to TEXT,
            FOREIGN KEY (origin_planet) REFERENCES planets(planet_id),
            FOREIGN KEY (destination_planet) REFERENCES planets(planet_id)
        );

        CREATE TABLE exchange_rates (
            rate_id TEXT PRIMARY KEY,
            source_currency TEXT NOT NULL,
            target_currency TEXT NOT NULL,
            rate REAL NOT NULL,
            effective_from TEXT NOT NULL,
            effective_to TEXT NOT NULL
        );

        CREATE TABLE shipping_quotes (
            quote_id TEXT PRIMARY KEY,
            creature_id TEXT NOT NULL,
            destination_planet TEXT NOT NULL,
            route_id TEXT NOT NULL,
            quote_date TEXT NOT NULL,
            quote_expiry TEXT NOT NULL,
            base_charge_usd REAL NOT NULL,
            mass_volume_charge_usd REAL NOT NULL,
            containment_charge_usd REAL NOT NULL,
            life_support_charge_usd REAL NOT NULL,
            customs_charge_usd REAL NOT NULL,
            total_quoted_usd REAL NOT NULL,
            currency TEXT NOT NULL,
            rate_version TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (creature_id) REFERENCES printed_creatures(creature_id),
            FOREIGN KEY (destination_planet) REFERENCES planets(planet_id),
            FOREIGN KEY (route_id) REFERENCES shipping_routes(route_id)
        );

        CREATE TABLE shipment_legs (
            leg_id TEXT PRIMARY KEY,
            quote_id TEXT NOT NULL,
            leg_number INTEGER NOT NULL,
            origin_planet TEXT NOT NULL,
            destination_planet TEXT NOT NULL,
            departure_date TEXT NOT NULL,
            arrival_date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (quote_id) REFERENCES shipping_quotes(quote_id),
            FOREIGN KEY (origin_planet) REFERENCES planets(planet_id),
            FOREIGN KEY (destination_planet) REFERENCES planets(planet_id)
        );

        CREATE TABLE shipment_events (
            event_id TEXT PRIMARY KEY,
            leg_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            event_date TEXT NOT NULL,
            source_sequence INTEGER NOT NULL,
            notes TEXT,
            FOREIGN KEY (leg_id) REFERENCES shipment_legs(leg_id)
        );

        CREATE TABLE actual_shipping_costs (
            cost_id TEXT PRIMARY KEY,
            leg_id TEXT NOT NULL,
            cost_category TEXT NOT NULL,
            amount_usd REAL NOT NULL,
            currency TEXT NOT NULL,
            actual_date TEXT NOT NULL,
            quote_id TEXT NOT NULL,
            FOREIGN KEY (leg_id) REFERENCES shipment_legs(leg_id),
            FOREIGN KEY (quote_id) REFERENCES shipping_quotes(quote_id)
        );
        """
    )

    connection.executemany(
        "INSERT INTO designers VALUES (?, ?, ?, ?)",
        DESIGNERS,
    )

    connection.executemany(
        "INSERT INTO designed_species VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (
                s["species_id"],
                s["designer_id"],
                s["design_name"],
                s.get("parent_species_1"),
                s.get("parent_species_2"),
                s["design_version"],
                s["created_date"],
                s["rule_version"],
            )
            for s in DESIGNED_SPECIES
        ],
    )

    connection.executemany(
        "INSERT INTO print_jobs VALUES (?, ?, ?, ?, ?, ?)",
        [
            (
                j["job_id"],
                j["species_id"],
                j["design_version"],
                j["ordered_date"],
                j["ordered_quantity"],
                j["completed_quantity"],
            )
            for j in PRINT_JOBS
        ],
    )

    connection.executemany(
        "INSERT INTO print_attempts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        PRINT_ATTEMPTS,
    )

    connection.executemany(
        "INSERT INTO printed_creatures VALUES (?, ?, ?, ?, ?, ?, ?)",
        PRINTED_CREATURES,
    )

    connection.executemany(
        "INSERT INTO universes VALUES (?, ?, ?, ?, ?)",
        UNIVERSES,
    )

    connection.executemany(
        "INSERT INTO planets VALUES (?, ?, ?, ?, ?, ?, ?)",
        PLANETS,
    )

    connection.executemany(
        "INSERT INTO habitat_requirements VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (
                r["requirement_id"],
                r["species_id"],
                r["temp_min_celsius"],
                r["temp_max_celsius"],
                r["pressure_kpa"],
                r["atmosphere"],
                r["gravity_g"],
                r["water_chemistry"],
                r["effective_from"],
                r.get("effective_to"),
                r["rule_version"],
            )
            for r in HABITAT_REQUIREMENTS
        ],
    )

    connection.executemany(
        "INSERT INTO habitat_capacity VALUES (?, ?, ?, ?, ?, ?)",
        HABITAT_CAPACITY,
    )

    connection.executemany(
        "INSERT INTO shipping_routes VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        SHIPPING_ROUTES,
    )

    connection.executemany(
        "INSERT INTO exchange_rates VALUES (?, ?, ?, ?, ?, ?)",
        EXCHANGE_RATES,
    )

    connection.executemany(
        "INSERT INTO shipping_quotes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (
                q["quote_id"],
                q["creature_id"],
                q["destination_planet"],
                q["route_id"],
                q["quote_date"],
                q["quote_expiry"],
                q["base_charge_usd"],
                q["mass_volume_charge_usd"],
                q["containment_charge_usd"],
                q["life_support_charge_usd"],
                q["customs_charge_usd"],
                q["total_quoted_usd"],
                q["currency"],
                q["rate_version"],
                q["status"],
            )
            for q in SHIPPING_QUOTES
        ],
    )

    connection.executemany(
        "INSERT INTO shipment_legs VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        SHIPMENT_LEGS,
    )

    connection.executemany(
        "INSERT INTO shipment_events VALUES (?, ?, ?, ?, ?, ?)",
        SHIPMENT_EVENTS,
    )

    connection.executemany(
        "INSERT INTO actual_shipping_costs VALUES (?, ?, ?, ?, ?, ?, ?)",
        ACTUAL_SHIPPING_COSTS,
    )


def generate_phase_four_dataset(path: str | Path) -> Path:
    """Create the SQLite phase-four designed-species and interplanetary dataset."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(output) as connection:
        create_phase_four_database(connection)
        connection.commit()
    return output


def summarize_phase_four(connection: sqlite3.Connection) -> dict[str, Any]:
    """Summarize designed-species production, shipping, and cost metrics."""
    designers = connection.execute("SELECT COUNT(*) FROM designers").fetchone()[0]
    designed_species = connection.execute("SELECT COUNT(*) FROM designed_species").fetchone()[0]
    print_jobs = connection.execute("SELECT COUNT(*) FROM print_jobs").fetchone()[0]
    total_attempts = connection.execute("SELECT COUNT(*) FROM print_attempts").fetchone()[0]
    successful_attempts = connection.execute(
        "SELECT COUNT(*) FROM print_attempts WHERE outcome = 'success'"
    ).fetchone()[0]
    failed_attempts = connection.execute(
        "SELECT COUNT(*) FROM print_attempts WHERE outcome = 'failed'"
    ).fetchone()[0]

    total_labor_cost = connection.execute(
        "SELECT COALESCE(SUM(labor_cost_usd), 0) FROM print_attempts"
    ).fetchone()[0]
    total_failed_cost = connection.execute(
        "SELECT COALESCE(SUM(failed_cost_usd), 0) FROM print_attempts"
    ).fetchone()[0]

    printed_creatures = connection.execute("SELECT COUNT(*) FROM printed_creatures").fetchone()[0]
    universes = connection.execute("SELECT COUNT(*) FROM universes").fetchone()[0]
    planets = connection.execute("SELECT COUNT(*) FROM planets").fetchone()[0]

    total_quoted_shipping = connection.execute(
        "SELECT COALESCE(SUM(total_quoted_usd), 0) FROM shipping_quotes"
    ).fetchone()[0]
    total_actual_shipping = connection.execute(
        "SELECT COALESCE(SUM(amount_usd), 0) FROM actual_shipping_costs"
    ).fetchone()[0]

    completed_shipments = connection.execute(
        "SELECT COUNT(*) FROM shipment_legs WHERE status = 'completed'"
    ).fetchone()[0]

    return {
        "designer_count": designers,
        "designed_species_count": designed_species,
        "print_job_count": print_jobs,
        "total_print_attempts": total_attempts,
        "successful_print_attempts": successful_attempts,
        "failed_print_attempts": failed_attempts,
        "total_production_labor_cost_usd": round(float(total_labor_cost), 2),
        "total_failed_production_cost_usd": round(float(total_failed_cost), 2),
        "printed_creatures_total": printed_creatures,
        "universe_count": universes,
        "planet_count": planets,
        "total_quoted_shipping_usd": round(float(total_quoted_shipping), 2),
        "total_actual_shipping_usd": round(float(total_actual_shipping), 2),
        "completed_shipment_legs": completed_shipments,
    }


def analyze_shipping_variance(connection: sqlite3.Connection) -> dict[str, Any]:
    """Analyze quote vs. actual shipping cost variance.

    Returns per-quote and aggregate variance, demonstrating cost reconciliation
    across versioned rate tables and multi-component charges.
    """
    variances = connection.execute(
        """
        SELECT
            q.quote_id,
            q.creature_id,
            q.total_quoted_usd,
            COALESCE(SUM(a.amount_usd), 0) AS actual_total_usd,
            COALESCE(SUM(a.amount_usd), 0) - q.total_quoted_usd AS variance_usd
        FROM shipping_quotes q
        LEFT JOIN actual_shipping_costs a ON a.quote_id = q.quote_id
        GROUP BY q.quote_id
        ORDER BY q.quote_id
        """
    ).fetchall()

    total_quoted = sum(v[2] for v in variances)
    total_actual = sum(v[3] for v in variances)
    aggregate_variance = total_actual - total_quoted

    return {
        "quote_variance_records": [
            {
                "quote_id": v[0],
                "creature_id": v[1],
                "quoted_usd": round(float(v[2]), 2),
                "actual_usd": round(float(v[3]), 2),
                "variance_usd": round(float(v[4]), 2),
            }
            for v in variances
        ],
        "total_quoted_usd": round(float(total_quoted), 2),
        "total_actual_usd": round(float(total_actual), 2),
        "aggregate_variance_usd": round(float(aggregate_variance), 2),
    }


def analyze_print_failure_costs(connection: sqlite3.Connection) -> dict[str, Any]:
    """Analyze failed print attempt costs by job and design.

    Demonstrates how failed production costs are tracked separately from
    successful labor and completed creature inventories.
    """
    failures = connection.execute(
        """
        SELECT
            pj.job_id,
            ds.design_name,
            ds.design_version,
            COUNT(pa.attempt_id) AS failed_count,
            COALESCE(SUM(pa.failed_cost_usd), 0) AS total_failed_cost_usd,
            GROUP_CONCAT(DISTINCT pa.failure_reason, ', ') AS reasons
        FROM print_jobs pj
        JOIN designed_species ds ON pj.species_id = ds.species_id
        JOIN print_attempts pa ON pj.job_id = pa.job_id AND pa.outcome = 'failed'
        GROUP BY pj.job_id
        ORDER BY pj.job_id
        """
    ).fetchall()

    return {
        "failed_jobs": [
            {
                "job_id": f[0],
                "design_name": f[1],
                "design_version": f[2],
                "failed_attempts": f[3],
                "total_failed_cost_usd": round(float(f[4]), 2),
                "failure_reasons": f[5],
            }
            for f in failures
        ],
        "total_failed_attempts_cost_usd": round(
            float(sum(f[4] for f in failures)),
            2,
        ),
    }


__all__ = [
    "DESIGNERS",
    "DESIGNED_SPECIES",
    "PRINT_JOBS",
    "PRINT_ATTEMPTS",
    "PRINTED_CREATURES",
    "UNIVERSES",
    "PLANETS",
    "HABITAT_REQUIREMENTS",
    "HABITAT_CAPACITY",
    "SHIPPING_ROUTES",
    "EXCHANGE_RATES",
    "SHIPPING_QUOTES",
    "SHIPMENT_LEGS",
    "SHIPMENT_EVENTS",
    "ACTUAL_SHIPPING_COSTS",
    "create_phase_four_database",
    "generate_phase_four_dataset",
    "summarize_phase_four",
    "analyze_shipping_variance",
    "analyze_print_failure_costs",
]
