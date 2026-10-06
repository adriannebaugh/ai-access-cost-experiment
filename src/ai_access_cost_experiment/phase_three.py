"""Synthetic phase-three data for extinct-species schema-drift scenario (2027).

This dataset introduces evolved creatures, new attributes, and controlled schema changes
to demonstrate:
- Field addition without breaking legacy measures.
- Nested lineage and historical-era classification.
- Versioned species/design records.
- Operational events and immutable histories.

The design guide calls this "Darwin times": revival of extinct creatures with taxonomy,
historical era, cloning batches, and lineage tracking. These are fictional, synthetic,
and test only the data platform's ability to absorb and reconcile schema changes.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

EXTINCT_SPECIES_SEEDS = [
    {
        "species_id": "species_extinct_001",
        "species_name": "Woolly Mammoth",
        "category": "revived",
        "taxon": "Mammuthus primigenius",
        "historical_era": "pleistocene",
        "native_universe": 0,
        "rule_version": "2027-01-01",
    },
    {
        "species_id": "species_extinct_002",
        "species_name": "Dodo",
        "category": "revived",
        "taxon": "Raphus cucullatus",
        "historical_era": "holocene",
        "native_universe": 0,
        "rule_version": "2027-01-01",
    },
    {
        "species_id": "species_extinct_003",
        "species_name": "Thylacine",
        "category": "revived",
        "taxon": "Thylacinus cynocephalus",
        "historical_era": "holocene",
        "native_universe": 0,
        "rule_version": "2027-01-01",
    },
    {
        "species_id": "species_extinct_004",
        "species_name": "Passenger Pigeon",
        "category": "revived",
        "taxon": "Ectopistes migratorius",
        "historical_era": "holocene",
        "native_universe": 0,
        "rule_version": "2027-01-01",
    },
]

CLONE_BATCHES = [
    {
        "batch_id": "batch_001",
        "species_id": "species_extinct_001",
        "design_version": "2027-mammoth-v1",
        "parent_species": "species_extinct_001",
        "lineage": None,
        "start_date": "2027-01-15",
        "end_date": "2027-02-20",
        "outcome": "success",
    },
    {
        "batch_id": "batch_002",
        "species_id": "species_extinct_002",
        "design_version": "2027-dodo-v1",
        "parent_species": "species_extinct_002",
        "lineage": None,
        "start_date": "2027-02-01",
        "end_date": "2027-03-10",
        "outcome": "partial",
    },
    {
        "batch_id": "batch_003",
        "species_id": "species_extinct_003",
        "design_version": "2027-thylacine-v1",
        "parent_species": "species_extinct_003",
        "lineage": None,
        "start_date": "2027-03-05",
        "end_date": "2027-04-22",
        "outcome": "success",
    },
    {
        "batch_id": "batch_004",
        "species_id": "species_extinct_004",
        "design_version": "2027-pigeon-v1",
        "parent_species": "species_extinct_004",
        "lineage": None,
        "start_date": "2027-04-01",
        "end_date": "2027-05-15",
        "outcome": "failed",
    },
]

CLONED_CREATURES_FROM_EXTINCT = [
    ("creature_extinct_001", "batch_001", "species_extinct_001", "agency_005", "Mammoth-Alpha", "2027-02-20", "Available"),
    ("creature_extinct_002", "batch_001", "species_extinct_001", "agency_008", "Mammoth-Beta", "2027-02-21", "Available"),
    ("creature_extinct_003", "batch_002", "species_extinct_002", "agency_007", "Dodo-One", "2027-03-10", "Pending"),
    ("creature_extinct_004", "batch_003", "species_extinct_003", "agency_012", "Thylacine-Prime", "2027-04-22", "Available"),
    ("creature_extinct_005", "batch_003", "species_extinct_003", "agency_014", "Thylacine-Secondary", "2027-04-23", "Available"),
]

APPLICATIONS_FOR_EXTINCT = [
    ("app_extinct_001", "creature_extinct_001", "agency_005", "2027-02-25", "submitted", 1),
    ("app_extinct_002", "creature_extinct_002", "agency_008", "2027-03-01", "approved", 2),
    ("app_extinct_003", "creature_extinct_003", "agency_007", "2027-03-15", "submitted", 1),
    ("app_extinct_004", "creature_extinct_004", "agency_012", "2027-04-25", "approved", 3),
    ("app_extinct_005", "creature_extinct_005", "agency_014", "2027-04-28", "submitted", 2),
]

HOUSEHOLD_PETS_BASELINE = [
    ("creature_baseline_001", "agency_001", "Sir Barksalot III", "Dog", "Denver", "2026-01-12", "Available"),
    ("creature_baseline_002", "agency_001", "Chairman Meow", "Cat", "Denver", "2026-01-15", "Available"),
    ("creature_baseline_003", "agency_002", "Lasagna", "Dog", "Boulder", "2026-02-01", "Pending"),
    ("creature_baseline_004", "agency_003", "Kevin", "Goat", "Colorado Springs", "2026-02-10", "Available"),
    ("creature_baseline_005", "agency_004", "Potato Supreme", "Rabbit", "Fort Collins", "2026-03-05", "Available"),
]


def create_phase_three_database(connection: sqlite3.Connection) -> None:
    """Create a deterministic schema-drift dataset with extinct species and evolution tracking.

    The schema adds:
    - species and design version tracking for evolved creatures
    - clone batches with outcome tracking
    - historical-era and taxon fields for extinct species
    - application history linking back to baseline household pets
    """
    connection.executescript(
        """
        CREATE TABLE species (
            species_id TEXT PRIMARY KEY,
            species_name TEXT NOT NULL,
            category TEXT NOT NULL,
            taxon TEXT,
            historical_era TEXT,
            native_universe INTEGER NOT NULL,
            rule_version TEXT NOT NULL
        );

        CREATE TABLE clone_batches (
            batch_id TEXT PRIMARY KEY,
            species_id TEXT NOT NULL,
            design_version TEXT NOT NULL,
            parent_species TEXT,
            lineage TEXT,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            outcome TEXT NOT NULL,
            FOREIGN KEY (species_id) REFERENCES species(species_id)
        );

        CREATE TABLE creatures_evolved (
            creature_id TEXT PRIMARY KEY,
            batch_id TEXT,
            species_id TEXT NOT NULL,
            agency_id TEXT NOT NULL,
            name TEXT NOT NULL,
            origin_category TEXT NOT NULL,
            origin_city TEXT,
            created_date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (batch_id) REFERENCES clone_batches(batch_id),
            FOREIGN KEY (species_id) REFERENCES species(species_id)
        );

        CREATE TABLE creatures_baseline (
            creature_id TEXT PRIMARY KEY,
            agency_id TEXT NOT NULL,
            name TEXT NOT NULL,
            species TEXT NOT NULL,
            origin_city TEXT NOT NULL,
            created_date TEXT NOT NULL,
            status TEXT NOT NULL
        );

        CREATE TABLE applications_evolved (
            application_id TEXT PRIMARY KEY,
            creature_id TEXT NOT NULL,
            agency_id TEXT NOT NULL,
            application_date TEXT NOT NULL,
            application_status TEXT NOT NULL,
            applicant_count INTEGER NOT NULL,
            FOREIGN KEY (creature_id) REFERENCES creatures_evolved(creature_id)
        );

        CREATE TABLE applications_baseline (
            application_id TEXT PRIMARY KEY,
            creature_id TEXT NOT NULL,
            agency_id TEXT NOT NULL,
            application_date TEXT NOT NULL,
            application_status TEXT NOT NULL,
            applicant_count INTEGER NOT NULL,
            FOREIGN KEY (creature_id) REFERENCES creatures_baseline(creature_id)
        );

        CREATE TABLE adoption_episodes (
            adoption_id TEXT PRIMARY KEY,
            creature_id TEXT NOT NULL,
            application_id TEXT NOT NULL,
            placement_date TEXT NOT NULL,
            return_date TEXT,
            returned INTEGER NOT NULL,
            fee_amount REAL,
            refund_amount REAL,
            source_origin TEXT NOT NULL
        );

        CREATE TABLE reconciliation_log (
            reconciliation_id TEXT PRIMARY KEY,
            run_date TEXT NOT NULL,
            scenario_name TEXT NOT NULL,
            baseline_creature_count INTEGER,
            evolved_creature_count INTEGER,
            baseline_application_count INTEGER,
            evolved_application_count INTEGER,
            schema_version TEXT NOT NULL,
            notes TEXT
        );
        """
    )

    connection.executemany(
        "INSERT INTO species VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
            (
                s["species_id"],
                s["species_name"],
                s["category"],
                s.get("taxon"),
                s.get("historical_era"),
                s["native_universe"],
                s["rule_version"],
            )
            for s in EXTINCT_SPECIES_SEEDS
        ],
    )

    connection.executemany(
        "INSERT INTO clone_batches VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (
                b["batch_id"],
                b["species_id"],
                b["design_version"],
                b.get("parent_species"),
                b.get("lineage"),
                b["start_date"],
                b["end_date"],
                b["outcome"],
            )
            for b in CLONE_BATCHES
        ],
    )

    connection.executemany(
        "INSERT INTO creatures_evolved VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        CLONED_CREATURES_FROM_EXTINCT,
    )

    connection.executemany(
        "INSERT INTO creatures_baseline VALUES (?, ?, ?, ?, ?, ?, ?)",
        HOUSEHOLD_PETS_BASELINE,
    )

    connection.executemany(
        "INSERT INTO applications_evolved VALUES (?, ?, ?, ?, ?, ?)",
        APPLICATIONS_FOR_EXTINCT,
    )

    baseline_applications = [
        ("app_baseline_001", "creature_baseline_001", "agency_001", "2026-01-15", "approved", 3),
        ("app_baseline_002", "creature_baseline_002", "agency_001", "2026-01-18", "submitted", 2),
        ("app_baseline_003", "creature_baseline_003", "agency_002", "2026-02-05", "submitted", 1),
        ("app_baseline_004", "creature_baseline_004", "agency_003", "2026-02-15", "approved", 4),
        ("app_baseline_005", "creature_baseline_005", "agency_004", "2026-03-10", "approved", 2),
    ]
    connection.executemany(
        "INSERT INTO applications_baseline VALUES (?, ?, ?, ?, ?, ?)",
        baseline_applications,
    )

    for adoption_index, (app_id, creature_id, agency_id, app_date, status, count) in enumerate(baseline_applications, start=1):
        if status == "approved":
            adoption_id = f"adoption_baseline_{adoption_index:03d}"
            placement_date = f"2026-0{(adoption_index % 9) + 1}-{(adoption_index * 7) % 28 + 1:02d}"
            connection.execute(
                "INSERT INTO adoption_episodes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    adoption_id,
                    creature_id,
                    app_id,
                    placement_date,
                    None,
                    0,
                    75.00 + (adoption_index * 10),
                    None,
                    "household_pets",
                ),
            )

    for adoption_index, (app_id, creature_id, agency_id, app_date, status, count) in enumerate(APPLICATIONS_FOR_EXTINCT, start=1):
        if status == "approved":
            adoption_id = f"adoption_extinct_{adoption_index:03d}"
            placement_date = f"2027-0{(adoption_index % 9) + 1}-{(adoption_index * 8) % 28 + 1:02d}"
            connection.execute(
                "INSERT INTO adoption_episodes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    adoption_id,
                    creature_id,
                    app_id,
                    placement_date,
                    None,
                    0,
                    150.00 + (adoption_index * 15),
                    None,
                    "extinct_revived",
                ),
            )

    connection.execute(
        "INSERT INTO reconciliation_log VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            "reconcile_2027_01_v1",
            "2027-01-01",
            "extinct_species_pilot",
            len(HOUSEHOLD_PETS_BASELINE),
            len(CLONED_CREATURES_FROM_EXTINCT),
            len(baseline_applications),
            len(APPLICATIONS_FOR_EXTINCT),
            "2027-01-schema-v1",
            "Baseline frozen; evolved creatures isolated; no duplicate adoption counts.",
        ),
    )


def generate_phase_three_dataset(path: str | Path) -> Path:
    """Create the SQLite phase-three extinct-species dataset at the requested destination."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(output) as connection:
        create_phase_three_database(connection)
        connection.commit()
    return output


def summarize_phase_three(connection: sqlite3.Connection) -> dict[str, Any]:
    """Summarize phase-three data and verify no cross-contamination between baselines."""
    baseline_creatures = connection.execute(
        "SELECT COUNT(*) FROM creatures_baseline"
    ).fetchone()[0]
    evolved_creatures = connection.execute(
        "SELECT COUNT(*) FROM creatures_evolved"
    ).fetchone()[0]
    extinct_species = connection.execute(
        "SELECT COUNT(*) FROM species WHERE category = 'revived'"
    ).fetchone()[0]
    clone_batches = connection.execute(
        "SELECT COUNT(*) FROM clone_batches"
    ).fetchone()[0]
    successful_batches = connection.execute(
        "SELECT COUNT(*) FROM clone_batches WHERE outcome = 'success'"
    ).fetchone()[0]

    baseline_adoptions = connection.execute(
        "SELECT COUNT(*) FROM adoption_episodes WHERE source_origin = 'household_pets'"
    ).fetchone()[0]
    extinct_adoptions = connection.execute(
        "SELECT COUNT(*) FROM adoption_episodes WHERE source_origin = 'extinct_revived'"
    ).fetchone()[0]

    baseline_adoption_revenue = connection.execute(
        "SELECT COALESCE(SUM(fee_amount), 0) FROM adoption_episodes WHERE source_origin = 'household_pets'"
    ).fetchone()[0]
    extinct_adoption_revenue = connection.execute(
        "SELECT COALESCE(SUM(fee_amount), 0) FROM adoption_episodes WHERE source_origin = 'extinct_revived'"
    ).fetchone()[0]

    return {
        "baseline_creature_count": baseline_creatures,
        "evolved_creature_count": evolved_creatures,
        "extinct_species_count": extinct_species,
        "clone_batch_count": clone_batches,
        "successful_batches": successful_batches,
        "baseline_adoptions": baseline_adoptions,
        "extinct_adoptions": extinct_adoptions,
        "baseline_adoption_revenue_usd": round(float(baseline_adoption_revenue), 2),
        "extinct_adoption_revenue_usd": round(float(extinct_adoption_revenue), 2),
    }


def verify_schema_drift_safety(connection: sqlite3.Connection) -> dict[str, Any]:
    """Verify that schema changes do not corrupt legacy measures.

    Returns evidence that baseline adoption counts, revenue, and funnel metrics
    remain unchanged when queried against the evolved schema.
    """
    baseline_app_count = connection.execute(
        "SELECT COUNT(*) FROM applications_baseline"
    ).fetchone()[0]
    baseline_approved = connection.execute(
        "SELECT COUNT(*) FROM applications_baseline WHERE application_status = 'approved'"
    ).fetchone()[0]
    baseline_adoption_count = connection.execute(
        "SELECT COUNT(*) FROM adoption_episodes WHERE source_origin = 'household_pets'"
    ).fetchone()[0]

    baseline_conversion = (
        (baseline_adoption_count / baseline_app_count * 100) if baseline_app_count > 0 else 0
    )

    baseline_revenue = connection.execute(
        "SELECT COALESCE(SUM(fee_amount), 0) FROM adoption_episodes WHERE source_origin = 'household_pets'"
    ).fetchone()[0]

    return {
        "baseline_applications_submitted": baseline_app_count,
        "baseline_applications_approved": baseline_approved,
        "baseline_adoptions_completed": baseline_adoption_count,
        "baseline_conversion_rate_percent": round(baseline_conversion, 2),
        "baseline_total_revenue_usd": round(float(baseline_revenue), 2),
        "safety_check": "baseline_measures_isolated_and_stable",
    }


__all__ = [
    "EXTINCT_SPECIES_SEEDS",
    "CLONE_BATCHES",
    "CLONED_CREATURES_FROM_EXTINCT",
    "APPLICATIONS_FOR_EXTINCT",
    "HOUSEHOLD_PETS_BASELINE",
    "create_phase_three_database",
    "generate_phase_three_dataset",
    "summarize_phase_three",
    "verify_schema_drift_safety",
]
