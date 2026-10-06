"""Synthetic next-phase data for the Colorado and national coverage scenarios."""

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

US_STATES = [
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Connecticut",
    "Delaware",
    "District of Columbia",
    "Florida",
    "Georgia",
    "Hawaii",
    "Idaho",
    "Illinois",
    "Indiana",
    "Iowa",
    "Kansas",
    "Kentucky",
    "Louisiana",
    "Maine",
    "Maryland",
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Nebraska",
    "Nevada",
    "New Hampshire",
    "New Jersey",
    "New Mexico",
    "New York",
    "North Carolina",
    "North Dakota",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "Pennsylvania",
    "Rhode Island",
    "South Carolina",
    "South Dakota",
    "Tennessee",
    "Texas",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West Virginia",
    "Wisconsin",
    "Wyoming",
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

NATIONAL_AGENCIES = [
    ("agency_101", "Pacific Northwest Network", "Seattle", "Washington", "2026-06-01"),
    ("agency_102", "Cascade Valley Center", "Portland", "Oregon", "2026-06-15"),
    ("agency_103", "Golden State Homes", "Los Angeles", "California", "2026-06-30"),
    ("agency_104", "Desert Horizon Rescue", "Phoenix", "Arizona", "2026-07-06"),
    ("agency_105", "Mountain West Collective", "Denver", "Colorado", "2026-07-13"),
    ("agency_106", "Great Plains Haven", "Omaha", "Nebraska", "2026-07-20"),
    ("agency_107", "Lake Shore Adoption", "Chicago", "Illinois", "2026-07-27"),
    ("agency_108", "Midwest Habitat Network", "Detroit", "Michigan", "2026-08-03"),
    ("agency_109", "Atlantic Coast Bridge", "Boston", "Massachusetts", "2026-08-10"),
    ("agency_110", "Sunrise South Homes", "Atlanta", "Georgia", "2026-08-17"),
    ("agency_111", "Gulf Coast Pairing", "Houston", "Texas", "2026-08-24"),
    ("agency_112", "Southeast River Rescue", "Nashville", "Tennessee", "2026-08-31"),
    ("agency_113", "Appalachian Care", "Charleston", "West Virginia", "2026-09-07"),
    ("agency_114", "Capital Region Adoption", "Washington", "District of Columbia", "2026-09-14"),
    ("agency_115", "Chesapeake Homes", "Baltimore", "Maryland", "2026-09-21"),
    ("agency_116", "Northern Woods Center", "Minneapolis", "Minnesota", "2026-09-28"),
    ("agency_117", "Heartland Safe Haven", "Kansas City", "Missouri", "2026-10-05"),
    ("agency_118", "Pine Ridge Pairings", "Bismarck", "North Dakota", "2026-10-12"),
    ("agency_119", "Frontier Renewal", "Boise", "Idaho", "2026-10-19"),
    ("agency_120", "High Plains Transfer", "Cheyenne", "Wyoming", "2026-10-26"),
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


def _national_coverage_map() -> dict[str, str]:
    """Create a deterministic one-agency-per-state coverage map for the national model."""
    map_by_state: dict[str, str] = {}
    for index, state_name in enumerate(US_STATES):
        agency_id = NATIONAL_AGENCIES[index % len(NATIONAL_AGENCIES)][0]
        map_by_state[state_name] = agency_id
    return map_by_state


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


def create_national_coverage_database(connection: sqlite3.Connection) -> None:
    """Create a deterministic national-scale coverage dataset for the next design milestone."""
    connection.executescript(
        """
        CREATE TABLE geography_reference (
            geography_name TEXT PRIMARY KEY,
            geography_type TEXT NOT NULL,
            parent_geography TEXT,
            is_in_scope INTEGER NOT NULL
        );

        CREATE TABLE agencies (
            agency_id TEXT PRIMARY KEY,
            agency_name TEXT NOT NULL,
            city TEXT NOT NULL,
            state_name TEXT NOT NULL,
            launch_date TEXT NOT NULL
        );

        CREATE TABLE agency_service_area (
            agency_id TEXT NOT NULL,
            geography_name TEXT NOT NULL,
            active_from TEXT NOT NULL,
            active_to TEXT,
            PRIMARY KEY (agency_id, geography_name, active_from),
            FOREIGN KEY (agency_id) REFERENCES agencies(agency_id)
        );
        """
    )

    for state_name in US_STATES:
        connection.execute(
            "INSERT INTO geography_reference VALUES (?, ?, ?, ?)",
            (state_name, "state", "United States", 1),
        )

    for agency_id, agency_name, city, state_name, launch_date in NATIONAL_AGENCIES:
        connection.execute(
            "INSERT INTO agencies VALUES (?, ?, ?, ?, ?)",
            (agency_id, agency_name, city, state_name, launch_date),
        )

    coverage_map = _national_coverage_map()
    for state_name in US_STATES:
        agency_id = coverage_map[state_name]
        connection.execute(
            "INSERT INTO agency_service_area VALUES (?, ?, ?, ?)",
            (agency_id, state_name, "2026-12-31", None),
        )


def generate_phase_two_dataset(path: str | Path) -> Path:
    """Create the SQLite phase-two dataset at the requested destination."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(output) as connection:
        create_phase_two_database(connection)
        connection.commit()
    return output


def generate_national_coverage_dataset(path: str | Path) -> Path:
    """Create the SQLite national dataset at the requested destination."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(output) as connection:
        create_national_coverage_database(connection)
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


def summarize_national_coverage(connection: sqlite3.Connection) -> dict[str, Any]:
    states = connection.execute("SELECT COUNT(*) FROM geography_reference").fetchone()[0]
    agency_count = connection.execute("SELECT COUNT(*) FROM agencies").fetchone()[0]
    service_areas = connection.execute("SELECT COUNT(*) FROM agency_service_area").fetchone()[0]
    return {
        "state_count": states,
        "agency_count": agency_count,
        "service_area_rows": service_areas,
    }


__all__ = [
    "COLORADO_COUNTIES",
    "US_STATES",
    "PHASE_TWO_AGENCIES",
    "NATIONAL_AGENCIES",
    "COUNTY_COVERAGE_2026_06_30",
    "COUNTY_COVERAGE_2026_12_31",
    "create_phase_two_database",
    "create_national_coverage_database",
    "generate_phase_two_dataset",
    "generate_national_coverage_dataset",
    "summarize_phase_two",
    "summarize_national_coverage",
]
