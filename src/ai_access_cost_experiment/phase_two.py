"""Synthetic next-phase data for the Colorado expansion scenario."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

COLORADO_COUNTIES = [
    "Adams",
    "Alamosa",
    "Arapahoe",
    "Archuleta",
    "Baca",
    "Bent",
    "Boulder",
    "Broomfield",
    "Chaffee",
    "Cheyenne",
    "Clear Creek",
    "Conejos",
    "Costilla",
    "Crowley",
    "Custer",
    "Delta",
    "Denver",
    "Dolores",
    "Douglas",
    "Eagle",
    "Elbert",
    "El Paso",
    "Denver",
    "Fremont",
    "Garfield",
    "Gilpin",
    "Grand",
    "Gunnison",
    "Hinsdale",
    "Huerfano",
    "Jackson",
    "Jefferson",
    "Kiowa",
    "Kit Carson",
    "La Plata",
    "Lake",
    "Larimer",
    "Las Animas",
    "Lincoln",
    "Logan",
    "Mesa",
    "Mineral",
    "Moffat",
    "Montezuma",
    "Montrose",
    "Morgan",
    "Otero",
    "Ouray",
    "Park",
    "Phillips",
    "Pitkin",
    "Prowers",
    "Pueblo",
    "Rio Blanco",
    "Rio Grande",
    "Routt",
    "Saguache",
    "San Juan",
    "San Miguel",
    "Sedgwick",
    "Summit",
    "Teller",
    "Washington",
    "Weld",
    "Yuma",
]

PHASE_TWO_AGENCIES = [
    ("agency_001", "Denver Metro Adoption", "Denver", "Denver", "2026-01-10"),
    ("agency_002", "North Front Range Rescue", "Boulder", "Boulder", "2026-01-18"),
    ("agency_003", "Pikes Peak Pet Center", "Colorado Springs", "El Paso", "2026-02-04"),
    ("agency_004", "Foothills Haven", "Fort Collins", "Larimer", "2026-02-18"),
    ("agency_005", "Western Slope Network", "Grand Junction", "Mesa", "2026-03-03"),
    ("agency_006", "Mountain Valley Transfer", "Pueblo", "Pueblo", "2026-03-22"),
    ("agency_007", "San Juan Care Collective", "Durango", "La Plata", "2026-04-14"),
    ("agency_008", "Summit Habitat Connect", "Breckenridge", "Summit", "2026-05-02"),
    ("agency_009", "Eagle Corridor Care", "Eagle", "Eagle", "2026-06-11"),
    ("agency_010", "South Metro Adoption", "Aurora", "Arapahoe", "2026-07-01"),
    ("agency_011", "Northern Plains Center", "Sterling", "Logan", "2026-08-05"),
    ("agency_012", "High Country Homes", "Aspen", "Pitkin", "2026-09-16"),
    ("agency_013", "Tri-County Bridge", "Greeley", "Weld", "2026-10-01"),
    ("agency_014", "Southeast Network", "Lamar", "Prowers", "2026-10-19"),
    ("agency_015", "Canyon Country Adoption", "Montrose", "Montrose", "2026-11-06"),
    ("agency_016", "Plains to Peaks", "Fort Morgan", "Morgan", "2026-11-22"),
]

COUNTY_COVERAGE_2026_06_30 = {
    "Denver": "agency_001",
    "Adams": "agency_001",
    "Arapahoe": "agency_010",
    "Boulder": "agency_002",
    "El Paso": "agency_003",
    "Larimer": "agency_004",
    "Mesa": "agency_005",
    "Pueblo": "agency_006",
    "La Plata": "agency_007",
    "Summit": "agency_008",
    "Eagle": "agency_009",
    "Pitkin": "agency_012",
    "Weld": "agency_013",
}

COUNTY_COVERAGE_2026_12_31 = {
    "Adams": "agency_001",
    "Arapahoe": "agency_010",
    "Archuleta": "agency_007",
    "Baca": "agency_014",
    "Bent": "agency_014",
    "Boulder": "agency_002",
    "Broomfield": "agency_001",
    "Chaffee": "agency_006",
    "Cheyenne": "agency_011",
    "Clear Creek": "agency_008",
    "Conejos": "agency_007",
    "Costilla": "agency_007",
    "Crowley": "agency_014",
    "Custer": "agency_006",
    "Delta": "agency_005",
    "Denver": "agency_001",
    "Dolores": "agency_007",
    "Douglas": "agency_010",
    "Eagle": "agency_009",
    "Elbert": "agency_010",
    "El Paso": "agency_003",
    "Fremont": "agency_006",
    "Garfield": "agency_009",
    "Gilpin": "agency_002",
    "Grand": "agency_008",
    "Gunnison": "agency_005",
    "Hinsdale": "agency_007",
    "Huerfano": "agency_014",
    "Jackson": "agency_008",
    "Jefferson": "agency_001",
    "Kiowa": "agency_014",
    "Kit Carson": "agency_011",
    "La Plata": "agency_007",
    "Lake": "agency_008",
    "Larimer": "agency_004",
    "Las Animas": "agency_014",
    "Lincoln": "agency_011",
    "Logan": "agency_011",
    "Mesa": "agency_005",
    "Mineral": "agency_007",
    "Moffat": "agency_015",
    "Montezuma": "agency_007",
    "Montrose": "agency_015",
    "Morgan": "agency_016",
    "Otero": "agency_014",
    "Ouray": "agency_015",
    "Park": "agency_008",
    "Phillips": "agency_011",
    "Pitkin": "agency_012",
    "Prowers": "agency_014",
    "Pueblo": "agency_006",
    "Rio Blanco": "agency_015",
    "Rio Grande": "agency_007",
    "Routt": "agency_008",
    "Saguache": "agency_007",
    "San Juan": "agency_015",
    "San Miguel": "agency_015",
    "Sedgwick": "agency_011",
    "Summit": "agency_008",
    "Teller": "agency_003",
    "Washington": "agency_011",
    "Weld": "agency_013",
    "Yuma": "agency_011",
}

CREATURE_SEEDS = [
    ("Juno", "Dog", "Denver", "agency_001", "2026-01-12", "Available"),
    ("Mochi", "Cat", "Niwot", "agency_002", "2026-01-21", "Available"),
    ("Atlas", "Goat", "Colorado Springs", "agency_003", "2026-02-05", "Available"),
    ("Bramble", "Rabbit", "Fort Collins", "agency_004", "2026-02-21", "Available"),
    ("Oona", "Dog", "Grand Junction", "agency_005", "2026-03-08", "Available"),
    ("Clover", "Pig", "Pueblo", "agency_006", "2026-03-24", "Available"),
    ("Tundra", "Rabbit", "Durango", "agency_007", "2026-04-17", "Available"),
    ("Arrow", "Cat", "Breckenridge", "agency_008", "2026-05-03", "Available"),
    ("Vela", "Dog", "Eagle", "agency_009", "2026-06-13", "Available"),
    ("Pip", "Cat", "Aurora", "agency_010", "2026-07-02", "Available"),
    ("Juniper", "Dog", "Sterling", "agency_011", "2026-08-10", "Pending"),
    ("Maple", "Goat", "Aspen", "agency_012", "2026-09-18", "Available"),
    ("Rico", "Rabbit", "Greeley", "agency_013", "2026-10-02", "Available"),
    ("Lulu", "Pig", "Lamar", "agency_014", "2026-10-20", "Available"),
    ("Sol", "Dog", "Montrose", "agency_015", "2026-11-07", "Available"),
    ("Poppy", "Cat", "Fort Morgan", "agency_016", "2026-11-23", "Available"),
]


def create_phase_two_database(connection: sqlite3.Connection) -> None:
    """Create a deterministic synthetic Colorado expansion dataset."""
    connection.executescript(
        """
        CREATE TABLE agencies (
            agency_id TEXT PRIMARY KEY,
            agency_name TEXT NOT NULL,
            city TEXT NOT NULL,
            county TEXT NOT NULL,
            launch_date TEXT NOT NULL
        );

        CREATE TABLE county_coverage (
            snapshot_date TEXT NOT NULL,
            county TEXT NOT NULL,
            is_covered INTEGER NOT NULL,
            agency_id TEXT,
            PRIMARY KEY (snapshot_date, county)
        );

        CREATE TABLE creatures (
            creature_id TEXT PRIMARY KEY,
            agency_id TEXT NOT NULL,
            name TEXT NOT NULL,
            species TEXT NOT NULL,
            origin_city TEXT NOT NULL,
            created_date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (agency_id) REFERENCES agencies(agency_id)
        );

        CREATE TABLE applications (
            application_id TEXT PRIMARY KEY,
            creature_id TEXT NOT NULL,
            agency_id TEXT NOT NULL,
            application_date TEXT NOT NULL,
            application_status TEXT NOT NULL,
            applicant_count INTEGER NOT NULL,
            FOREIGN KEY (creature_id) REFERENCES creatures(creature_id),
            FOREIGN KEY (agency_id) REFERENCES agencies(agency_id)
        );

        CREATE TABLE application_events (
            event_id TEXT PRIMARY KEY,
            application_id TEXT NOT NULL,
            event_time TEXT NOT NULL,
            previous_status TEXT,
            new_status TEXT NOT NULL,
            source_sequence INTEGER NOT NULL,
            FOREIGN KEY (application_id) REFERENCES applications(application_id)
        );
        """
    )

    connection.executemany(
        "INSERT INTO agencies VALUES (?, ?, ?, ?, ?)",
        PHASE_TWO_AGENCIES,
    )

    for snapshot, coverage_map in (
        ("2026-06-30", COUNTY_COVERAGE_2026_06_30),
        ("2026-12-31", COUNTY_COVERAGE_2026_12_31),
    ):
        for county in COLORADO_COUNTIES:
            agency_id = coverage_map.get(county)
            connection.execute(
                "INSERT INTO county_coverage VALUES (?, ?, ?, ?)",
                (snapshot, county, 1 if agency_id else 0, agency_id),
            )

    for index, (name, species, city, agency_id, created_date) in enumerate(CREATURE_SEEDS, start=1):
        creature_id = f"creature_{index:03d}"
        connection.execute(
            "INSERT INTO creatures VALUES (?, ?, ?, ?, ?, ?, ?)",
            (creature_id, agency_id, name, species, city, created_date, "Available"),
        )

        app_id = f"app_{index:03d}"
        status = "submitted" if index % 3 else "approved"
        application_count = 2 + ((index * 3) % 6)
        connection.execute(
            "INSERT INTO applications VALUES (?, ?, ?, ?, ?, ?)",
            (
                app_id,
                creature_id,
                agency_id,
                created_date,
                status,
                application_count,
            ),
        )

        connection.execute(
            "INSERT INTO application_events VALUES (?, ?, ?, ?, ?, ?)",
            (
                f"event_{index:03d}_001",
                app_id,
                f"{created_date}T09:00:00Z",
                None,
                status,
                1,
            ),
        )


def generate_phase_two_dataset(path: str | Path) -> Path:
    """Create the SQLite phase-two dataset at the requested destination."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(output) as connection:
        create_phase_two_database(connection)
        connection.commit()
    return output


def summarize_phase_two(connection: sqlite3.Connection) -> dict[str, Any]:
    agencies = connection.execute("SELECT COUNT(*) FROM agencies").fetchone()[0]
    covered_june = connection.execute(
        "SELECT COUNT(*) FROM county_coverage WHERE snapshot_date = '2026-06-30' AND is_covered = 1"
    ).fetchone()[0]
    covered_dec = connection.execute(
        "SELECT COUNT(*) FROM county_coverage WHERE snapshot_date = '2026-12-31' AND is_covered = 1"
    ).fetchone()[0]
    uncovered_dec = connection.execute(
        "SELECT COUNT(*) FROM county_coverage WHERE snapshot_date = '2026-12-31' AND is_covered = 0"
    ).fetchone()[0]
    applications = connection.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    return {
        "agency_count": agencies,
        "covered_count_june_2026": covered_june,
        "covered_count_dec_2026": covered_dec,
        "uncovered_count_dec_2026": uncovered_dec,
        "application_count": applications,
    }


__all__ = [
    "COLORADO_COUNTIES",
    "PHASE_TWO_AGENCIES",
    "COUNTY_COVERAGE_2026_06_30",
    "COUNTY_COVERAGE_2026_12_31",
    "create_phase_two_database",
    "generate_phase_two_dataset",
    "summarize_phase_two",
]
