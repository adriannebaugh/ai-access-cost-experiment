import sqlite3

from ai_access_cost_experiment.phase_two import (
    COLORADO_COUNTIES,
    NATIONAL_AGENCIES,
    US_STATES,
    COUNTY_COVERAGE_2026_06_30,
    COUNTY_COVERAGE_2026_12_31,
    create_national_coverage_database,
    create_phase_two_database,
    generate_national_coverage_dataset,
    generate_phase_two_dataset,
    summarize_national_coverage,
    summarize_phase_two,
)


def test_phase_two_dataset_has_expected_synthetic_shape():
    with sqlite3.connect(":memory:") as connection:
        create_phase_two_database(connection)

        agency_count = connection.execute("SELECT COUNT(*) FROM agencies").fetchone()[0]
        county_june_covered = connection.execute(
            "SELECT COUNT(*) FROM county_coverage WHERE snapshot_date = '2026-06-30' AND is_covered = 1"
        ).fetchone()[0]
        county_dec_covered = connection.execute(
            "SELECT COUNT(*) FROM county_coverage WHERE snapshot_date = '2026-12-31' AND is_covered = 1"
        ).fetchone()[0]
        creature_count = connection.execute("SELECT COUNT(*) FROM creatures").fetchone()[0]
        application_count = connection.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
        event_count = connection.execute("SELECT COUNT(*) FROM application_events").fetchone()[0]

        assert agency_count == 16
        assert county_june_covered == len(COUNTY_COVERAGE_2026_06_30)
        assert county_dec_covered == len(COUNTY_COVERAGE_2026_12_31)
        assert county_dec_covered == len(COLORADO_COUNTIES)
        assert creature_count == 16
        assert application_count == 16
        assert event_count == 16

        summary = summarize_phase_two(connection)
        assert summary["agency_count"] == 16
        assert summary["covered_count_june_2026"] == len(COUNTY_COVERAGE_2026_06_30)
        assert summary["covered_count_dec_2026"] == len(COUNTY_COVERAGE_2026_12_31)
        assert summary["uncovered_count_dec_2026"] == 0
        assert summary["application_count"] == 16


def test_national_coverage_dataset_stays_deterministic_and_complete():
    with sqlite3.connect(":memory:") as connection:
        create_national_coverage_database(connection)

        state_count = connection.execute("SELECT COUNT(*) FROM geography_reference").fetchone()[0]
        agency_count = connection.execute("SELECT COUNT(*) FROM agencies").fetchone()[0]
        service_area_count = connection.execute(
            "SELECT COUNT(*) FROM agency_service_area"
        ).fetchone()[0]

        assert state_count == len(US_STATES)
        assert agency_count == len(NATIONAL_AGENCIES)
        assert service_area_count == len(US_STATES)

        summary = summarize_national_coverage(connection)
        assert summary["state_count"] == len(US_STATES)
        assert summary["agency_count"] == len(NATIONAL_AGENCIES)
        assert summary["service_area_rows"] == len(US_STATES)


def test_generate_phase_two_dataset_and_national_dataset_write_sqlite_files(tmp_path):
    phase_two_path = tmp_path / "phase_two.sqlite"
    national_path = tmp_path / "national_coverage.sqlite"

    generated_phase_two = generate_phase_two_dataset(phase_two_path)
    generated_national = generate_national_coverage_dataset(national_path)

    assert generated_phase_two == phase_two_path
    assert generated_national == national_path
    assert phase_two_path.exists()
    assert national_path.exists()

    with sqlite3.connect(phase_two_path) as phase_connection:
        assert phase_connection.execute("SELECT COUNT(*) FROM agencies").fetchone()[0] == 16

    with sqlite3.connect(national_path) as national_connection:
        assert national_connection.execute("SELECT COUNT(*) FROM agencies").fetchone()[0] == len(NATIONAL_AGENCIES)
