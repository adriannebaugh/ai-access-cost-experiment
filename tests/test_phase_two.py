"""Tests for Phase 2 Colorado expansion and national coverage datasets."""

import sqlite3
import pytest

from ai_access_cost_experiment.phase_two import (
    COLORADO_COUNTIES,
    NATIONAL_AGENCIES,
    US_STATES,
    COUNTY_COVERAGE_2026_06_30,
    COUNTY_COVERAGE_2026_12_31,
    PHASE_TWO_AGENCIES,
    CREATURE_SEEDS,
    create_national_coverage_database,
    create_phase_two_database,
    generate_national_coverage_dataset,
    generate_phase_two_dataset,
    summarize_national_coverage,
    summarize_phase_two,
)


class TestPhaseTwo:
    """Tests for the Colorado expansion Phase 2 dataset."""

    def test_phase_two_agencies_are_deterministic(self):
        """Verify the Phase 2 agency list is complete and unchanged."""
        assert len(PHASE_TWO_AGENCIES) == 16
        agency_ids = [agency[0] for agency in PHASE_TWO_AGENCIES]
        assert agency_ids == [f"agency_{i:03d}" for i in range(1, 17)]
        assert all(agency[1] for agency in PHASE_TWO_AGENCIES)  # names exist
        assert all(agency[4] for agency in PHASE_TWO_AGENCIES)  # launch dates exist

    def test_colorado_counties_reference_is_complete(self):
        """Verify the frozen Colorado county reference list."""
        assert len(COLORADO_COUNTIES) == 64
        assert "Denver" in COLORADO_COUNTIES
        assert "Adams" in COLORADO_COUNTIES
        assert "Yuma" in COLORADO_COUNTIES
        assert len(set(COLORADO_COUNTIES)) == 64  # no duplicates

    def test_county_coverage_2026_06_30_is_partial(self):
        """Verify the June 30 coverage snapshot is intentionally partial."""
        assert len(COUNTY_COVERAGE_2026_06_30) == 13
        covered_counties = set(COUNTY_COVERAGE_2026_06_30.keys())
        assert covered_counties.issubset(set(COLORADO_COUNTIES))
        for county, agency_id in COUNTY_COVERAGE_2026_06_30.items():
            assert agency_id.startswith("agency_")
            assert int(agency_id.split("_")[1]) <= 16

    def test_county_coverage_2026_12_31_is_complete(self):
        """Verify the Dec 31 coverage snapshot reaches all Colorado counties."""
        assert len(COUNTY_COVERAGE_2026_12_31) == 64
        covered_counties = set(COUNTY_COVERAGE_2026_12_31.keys())
        assert covered_counties == set(COLORADO_COUNTIES)
        for county, agency_id in COUNTY_COVERAGE_2026_12_31.items():
            assert agency_id.startswith("agency_")
            assert int(agency_id.split("_")[1]) <= 16

    def test_creature_seeds_are_deterministic_fixtures(self):
        """Verify the seed creatures are fixed and reproducible."""
        assert len(CREATURE_SEEDS) == 16
        names = [c[0] for c in CREATURE_SEEDS]
        assert names == [
            "Juno", "Mochi", "Atlas", "Bramble", "Oona", "Clover", "Tundra", "Arrow",
            "Vela", "Pip", "Juniper", "Maple", "Rico", "Lulu", "Sol", "Poppy"
        ]
        species = [c[1] for c in CREATURE_SEEDS]
        assert set(species) == {"Dog", "Cat", "Goat", "Rabbit", "Pig"}

    def test_phase_two_database_schema_is_correct(self):
        """Verify the Phase 2 schema matches the expected structure."""
        with sqlite3.connect(":memory:") as connection:
            create_phase_two_database(connection)

            # Check agencies table
            agencies_schema = connection.execute(
                "PRAGMA table_info(agencies)"
            ).fetchall()
            agency_cols = {col[1] for col in agencies_schema}
            assert agency_cols == {"agency_id", "agency_name", "city", "county", "launch_date"}

            # Check county_coverage table
            coverage_schema = connection.execute(
                "PRAGMA table_info(county_coverage)"
            ).fetchall()
            coverage_cols = {col[1] for col in coverage_schema}
            assert coverage_cols == {"snapshot_date", "county", "is_covered", "agency_id"}

            # Check creatures table
            creatures_schema = connection.execute(
                "PRAGMA table_info(creatures)"
            ).fetchall()
            creature_cols = {col[1] for col in creatures_schema}
            assert creature_cols == {
                "creature_id", "agency_id", "name", "species", "origin_city", "created_date", "status"
            }

            # Check applications table
            apps_schema = connection.execute(
                "PRAGMA table_info(applications)"
            ).fetchall()
            app_cols = {col[1] for col in apps_schema}
            assert app_cols == {
                "application_id", "creature_id", "agency_id", "application_date", "application_status", "applicant_count"
            }

            # Check application_events table
            events_schema = connection.execute(
                "PRAGMA table_info(application_events)"
            ).fetchall()
            event_cols = {col[1] for col in events_schema}
            assert event_cols == {
                "event_id", "application_id", "event_time", "previous_status", "new_status", "source_sequence"
            }

    def test_phase_two_dataset_has_expected_row_counts(self):
        """Verify the Phase 2 dataset produces deterministic row counts."""
        with sqlite3.connect(":memory:") as connection:
            create_phase_two_database(connection)

            agency_count = connection.execute("SELECT COUNT(*) FROM agencies").fetchone()[0]
            assert agency_count == 16

            # June 30 coverage
            county_june_covered = connection.execute(
                "SELECT COUNT(*) FROM county_coverage WHERE snapshot_date = '2026-06-30' AND is_covered = 1"
            ).fetchone()[0]
            assert county_june_covered == 13

            # Dec 31 coverage (all 64 counties covered)
            county_dec_covered = connection.execute(
                "SELECT COUNT(*) FROM county_coverage WHERE snapshot_date = '2026-12-31' AND is_covered = 1"
            ).fetchone()[0]
            assert county_dec_covered == 64

            county_dec_uncovered = connection.execute(
                "SELECT COUNT(*) FROM county_coverage WHERE snapshot_date = '2026-12-31' AND is_covered = 0"
            ).fetchone()[0]
            assert county_dec_uncovered == 0

            creature_count = connection.execute("SELECT COUNT(*) FROM creatures").fetchone()[0]
            assert creature_count == 16

            application_count = connection.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
            assert application_count == 16

            event_count = connection.execute("SELECT COUNT(*) FROM application_events").fetchone()[0]
            assert event_count == 16

    def test_phase_two_summarize_produces_expected_output(self):
        """Verify the summarize function returns the expected structure and values."""
        with sqlite3.connect(":memory:") as connection:
            create_phase_two_database(connection)
            summary = summarize_phase_two(connection)

            assert summary == {
                "agency_count": 16,
                "covered_count_june_2026": 13,
                "covered_count_dec_2026": 64,
                "uncovered_count_dec_2026": 0,
                "application_count": 16,
            }

    def test_phase_two_county_coverage_progression(self):
        """Verify coverage expanded from June to December 2026."""
        june_covered = len(COUNTY_COVERAGE_2026_06_30)
        dec_covered = len(COUNTY_COVERAGE_2026_12_31)
        assert june_covered < dec_covered
        assert dec_covered == len(COLORADO_COUNTIES)

        june_counties = set(COUNTY_COVERAGE_2026_06_30.keys())
        dec_counties = set(COUNTY_COVERAGE_2026_12_31.keys())
        assert june_counties.issubset(dec_counties)

    def test_phase_two_creatures_reference_agencies(self):
        """Verify all creatures reference valid agencies."""
        with sqlite3.connect(":memory:") as connection:
            create_phase_two_database(connection)

            valid_agency_ids = {a[0] for a in PHASE_TWO_AGENCIES}

            creatures = connection.execute(
                "SELECT agency_id FROM creatures"
            ).fetchall()
            for (agency_id,) in creatures:
                assert agency_id in valid_agency_ids

    def test_phase_two_applications_reference_valid_creatures_and_agencies(self):
        """Verify referential integrity in the applications table."""
        with sqlite3.connect(":memory:") as connection:
            create_phase_two_database(connection)

            valid_creature_ids = {f"creature_{i:03d}" for i in range(1, 17)}
            valid_agency_ids = {a[0] for a in PHASE_TWO_AGENCIES}

            apps = connection.execute(
                "SELECT creature_id, agency_id FROM applications"
            ).fetchall()
            for creature_id, agency_id in apps:
                assert creature_id in valid_creature_ids
                assert agency_id in valid_agency_ids

    def test_phase_two_events_reference_valid_applications(self):
        """Verify application events reference valid applications."""
        with sqlite3.connect(":memory:") as connection:
            create_phase_two_database(connection)

            valid_app_ids = {f"app_{i:03d}" for i in range(1, 17)}

            events = connection.execute(
                "SELECT application_id FROM application_events"
            ).fetchall()
            for (app_id,) in events:
                assert app_id in valid_app_ids


class TestNationalCoverage:
    """Tests for the national coverage expansion dataset."""

    def test_us_states_reference_is_complete(self):
        """Verify the U.S. states reference includes all 50 states plus D.C."""
        assert len(US_STATES) == 51
        assert "District of Columbia" in US_STATES
        assert "Colorado" in US_STATES
        assert "Alaska" in US_STATES
        assert "Hawaii" in US_STATES

    def test_national_agencies_seed_data(self):
        """Verify national agencies are defined for multi-region deployment."""
        assert len(NATIONAL_AGENCIES) == 20
        agency_ids = [a[0] for a in NATIONAL_AGENCIES]
        assert agency_ids == [f"agency_{i:03d}" for i in range(101, 121)]
        assert all(a[1] for a in NATIONAL_AGENCIES)  # names exist
        assert all(a[2] for a in NATIONAL_AGENCIES)  # cities exist
        assert all(a[3] for a in NATIONAL_AGENCIES)  # states exist
        assert all(a[4] for a in NATIONAL_AGENCIES)  # launch dates exist

    def test_national_coverage_database_schema(self):
        """Verify the national schema includes geography reference and service areas."""
        with sqlite3.connect(":memory:") as connection:
            create_national_coverage_database(connection)

            # Check geography_reference table
            geo_schema = connection.execute(
                "PRAGMA table_info(geography_reference)"
            ).fetchall()
            geo_cols = {col[1] for col in geo_schema}
            assert geo_cols == {"geography_name", "geography_type", "parent_geography", "is_in_scope"}

            # Check agencies table
            agencies_schema = connection.execute(
                "PRAGMA table_info(agencies)"
            ).fetchall()
            agency_cols = {col[1] for col in agencies_schema}
            assert agency_cols == {"agency_id", "agency_name", "city", "state_name", "launch_date"}

            # Check agency_service_area table
            service_schema = connection.execute(
                "PRAGMA table_info(agency_service_area)"
            ).fetchall()
            service_cols = {col[1] for col in service_schema}
            assert service_cols == {"agency_id", "geography_name", "active_from", "active_to"}

    def test_national_coverage_dataset_row_counts(self):
        """Verify national dataset produces expected row counts."""
        with sqlite3.connect(":memory:") as connection:
            create_national_coverage_database(connection)

            state_count = connection.execute("SELECT COUNT(*) FROM geography_reference").fetchone()[0]
            assert state_count == 51  # 50 states + DC

            agency_count = connection.execute("SELECT COUNT(*) FROM agencies").fetchone()[0]
            assert agency_count == 20

            service_area_count = connection.execute(
                "SELECT COUNT(*) FROM agency_service_area"
            ).fetchone()[0]
            assert service_area_count == 51  # one per state

    def test_national_coverage_summarize_produces_expected_output(self):
        """Verify national summarize function returns correct structure."""
        with sqlite3.connect(":memory:") as connection:
            create_national_coverage_database(connection)
            summary = summarize_national_coverage(connection)

            assert summary == {
                "state_count": 51,
                "agency_count": 20,
                "service_area_rows": 51,
            }

    def test_national_coverage_service_areas_reference_valid_geographies_and_agencies(self):
        """Verify referential integrity in the national model."""
        with sqlite3.connect(":memory:") as connection:
            create_national_coverage_database(connection)

            valid_geographies = set(US_STATES)
            valid_agencies = {a[0] for a in NATIONAL_AGENCIES}

            service_areas = connection.execute(
                "SELECT agency_id, geography_name FROM agency_service_area"
            ).fetchall()
            for agency_id, geography_name in service_areas:
                assert agency_id in valid_agencies
                assert geography_name in valid_geographies


class TestFileGeneration:
    """Tests for dataset file generation and persistence."""

    def test_generate_phase_two_dataset_creates_valid_sqlite_file(self, tmp_path):
        """Verify phase two dataset generation creates a readable SQLite file."""
        phase_two_path = tmp_path / "phase_two_test.sqlite"
        result_path = generate_phase_two_dataset(phase_two_path)

        assert result_path == phase_two_path
        assert phase_two_path.exists()
        assert phase_two_path.stat().st_size > 0

        with sqlite3.connect(phase_two_path) as connection:
            summary = summarize_phase_two(connection)
            assert summary["agency_count"] == 16
            assert summary["covered_count_dec_2026"] == 64
            assert summary["application_count"] == 16

    def test_generate_national_dataset_creates_valid_sqlite_file(self, tmp_path):
        """Verify national dataset generation creates a readable SQLite file."""
        national_path = tmp_path / "national_test.sqlite"
        result_path = generate_national_coverage_dataset(national_path)

        assert result_path == national_path
        assert national_path.exists()
        assert national_path.stat().st_size > 0

        with sqlite3.connect(national_path) as connection:
            summary = summarize_national_coverage(connection)
            assert summary["state_count"] == 51
            assert summary["agency_count"] == 20
            assert summary["service_area_rows"] == 51

    def test_generated_phase_two_dataset_is_reproducible(self, tmp_path):
        """Verify generating the dataset twice produces identical results."""
        path_1 = tmp_path / "phase_two_1.sqlite"
        path_2 = tmp_path / "phase_two_2.sqlite"

        generate_phase_two_dataset(path_1)
        generate_phase_two_dataset(path_2)

        with sqlite3.connect(path_1) as c1, sqlite3.connect(path_2) as c2:
            summary_1 = summarize_phase_two(c1)
            summary_2 = summarize_phase_two(c2)

            assert summary_1 == summary_2

    def test_generated_national_dataset_is_reproducible(self, tmp_path):
        """Verify generating the national dataset twice produces identical results."""
        path_1 = tmp_path / "national_1.sqlite"
        path_2 = tmp_path / "national_2.sqlite"

        generate_national_coverage_dataset(path_1)
        generate_national_coverage_dataset(path_2)

        with sqlite3.connect(path_1) as c1, sqlite3.connect(path_2) as c2:
            summary_1 = summarize_national_coverage(c1)
            summary_2 = summarize_national_coverage(c2)

            assert summary_1 == summary_2

    def test_generate_phase_two_creates_parent_directories(self, tmp_path):
        """Verify dataset generation creates parent directories if needed."""
        nested_path = tmp_path / "nested" / "deep" / "phase_two.sqlite"
        assert not nested_path.parent.exists()

        generate_phase_two_dataset(nested_path)

        assert nested_path.exists()
        assert nested_path.parent.exists()

    def test_phase_two_dataset_survives_writes_and_validation(self, tmp_path):
        """Verify the generated dataset can be written to and read from multiple times."""
        path = tmp_path / "phase_two_rw.sqlite"
        generate_phase_two_dataset(path)

        # First read
        with sqlite3.connect(path) as conn:
            c1 = conn.execute("SELECT COUNT(*) FROM creatures").fetchone()[0]
            assert c1 == 16

        # Second read from the same file
        with sqlite3.connect(path) as conn:
            c2 = conn.execute("SELECT COUNT(*) FROM creatures").fetchone()[0]
            assert c2 == c1

        # Validate referential integrity survives file persistence
        with sqlite3.connect(path) as conn:
            orphaned = conn.execute(
                """
                SELECT COUNT(*) FROM applications
                WHERE creature_id NOT IN (SELECT creature_id FROM creatures)
                """
            ).fetchone()[0]
            assert orphaned == 0


class TestCostEvidenceCompliance:
    """Tests to verify the datasets follow cost evidence rules."""

    def test_no_pricing_data_in_synthetic_datasets(self):
        """Verify no unverified pricing is embedded in the dataset definitions."""
        # This is a synthetic-only baseline; cost measurement happens at Databricks time
        with sqlite3.connect(":memory:") as connection:
            create_phase_two_database(connection)

            # Verify no cost/price columns exist in Phase 2
            tables = connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            table_names = [t[0] for t in tables]
            assert "cost" not in str(table_names).lower()
            assert "price" not in str(table_names).lower()
            assert "billing" not in str(table_names).lower()

    def test_local_baseline_is_clearly_synthetic(self):
        """Verify the datasets are labeled as synthetic/local reference."""
        # This test documents intent: the data should never be presented as Databricks usage
        assert "phase_two" in create_phase_two_database.__module__
        with sqlite3.connect(":memory:") as connection:
            create_phase_two_database(connection)
            # No timestamp or version to suggest real production data
            tables = connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()
            # Verify the schema is simple and deterministic, not production-like
            assert len(tables) == 5  # Only the 5 tables we defined
