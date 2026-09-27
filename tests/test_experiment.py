import json
import sqlite3
import pytest

from ai_access_cost_experiment.cli import run_local
from ai_access_cost_experiment.dataset import create_database
from ai_access_cost_experiment.ledger import read_records, summarize
from ai_access_cost_experiment.questions import answer_question


def test_deterministic_answers():
    with sqlite3.connect(":memory:") as connection:
        create_database(connection)
        assert answer_question(connection, "q1") == "5 available pets have chaos above 8."
        assert answer_question(connection, "q2") == "Dumpster Fire, Gary, Wi-Fi Password"
        assert "not causal" in answer_question(connection, "q3")
        assert "11 applications" in answer_question(connection, "q4")
        assert "explicit demo rule" in answer_question(connection, "q5")


def test_run_records_unknown_cost_not_zero(tmp_path):
    ledger_path = tmp_path / "runs.jsonl"
    run_local(ledger_path)

    records = read_records(ledger_path)
    report = summarize(records)
    assert len(records) == 5
    assert report["cost_components"] == {"observed": 0, "estimated": 0, "unknown": 5}
    assert all(record["cost_components"][0]["amount"] is None for record in records)
    assert all(
        json.loads(line)["run_id"] == records[0]["run_id"]
        for line in ledger_path.read_text().splitlines()
    )


def test_platform_probes_record_usage_and_unknown_cost(tmp_path, monkeypatch):
    from ai_access_cost_experiment import platforms

    class Cursor:
        def execute(self, query):
            assert query == "SELECT current_user(), current_catalog(), current_schema()"

        def fetchone(self):
            return ("service-principal", "main", "default")

        def close(self):
            pass

    class Connection:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def cursor(self):
            return Cursor()

    monkeypatch.setattr(platforms, "_connect_databricks", lambda config: Connection())
    databricks_record = platforms.probe_databricks(
        tmp_path / "databricks.jsonl",
        {
            "DATABRICKS_SERVER_HOSTNAME": "dbc.example.cloud.databricks.com",
            "DATABRICKS_HTTP_PATH": "/sql/warehouse/test",
            "DATABRICKS_TOKEN": "not-a-real-token",
        },
    )
    assert databricks_record["answer"]["principal"] == "service-principal"
    assert databricks_record["usage_observations"][0]["amount"] == 1
    assert databricks_record["cost_components"][0]["status"] == "unknown"
    assert "not-a-real-token" not in json.dumps(databricks_record)


def test_salesforce_probe_uses_version_and_limits_only(tmp_path, monkeypatch):
    from ai_access_cost_experiment import platforms

    requested_urls = []

    class Response:
        def __init__(self, payload):
            self.payload = payload

        def raise_for_status(self):
            pass

        def json(self):
            return self.payload

    def fake_get(url, access_token):
        assert access_token == "not-a-real-token"
        requested_urls.append(url)
        if url.endswith("/services/data/"):
            return Response([{"version": "65.0"}, {"version": "66.0"}])
        return Response({"DailyApiRequests": {"Max": 100000, "Remaining": 99998}})

    monkeypatch.setattr(platforms, "_salesforce_get", fake_get)
    ledger_path = tmp_path / "salesforce.jsonl"
    record = platforms.probe_salesforce(
        ledger_path,
        {
            "SALESFORCE_INSTANCE_URL": "https://example.my.salesforce.com",
            "SALESFORCE_ACCESS_TOKEN": "not-a-real-token",
        },
    )
    assert requested_urls == [
        "https://example.my.salesforce.com/services/data/",
        "https://example.my.salesforce.com/services/data/v66.0/limits",
    ]
    assert record["answer"]["daily_api_requests"]["remaining"] == 99998
    assert record["usage_observations"][0]["amount"] == 2
    assert record["cost_components"][0]["status"] == "unknown"


def test_salesforce_rejects_lightning_ui_url(tmp_path):
    from ai_access_cost_experiment.platforms import (
        PlatformConfigurationError,
        probe_salesforce,
    )

    with pytest.raises(PlatformConfigurationError, match="not a Lightning page URL"):
        probe_salesforce(
            tmp_path / "runs.jsonl",
            {
                "SALESFORCE_INSTANCE_URL": "https://example.lightning.force.com",
                "SALESFORCE_ACCESS_TOKEN": "not-a-real-token",
            },
        )


def test_failed_databricks_connection_is_ledgered_as_unknown_cost(
    tmp_path, monkeypatch
):
    from ai_access_cost_experiment import platforms

    def failed_connection(config):
        raise TimeoutError

    monkeypatch.setattr(platforms, "_connect_databricks", failed_connection)
    ledger_path = tmp_path / "failed.jsonl"
    with pytest.raises(platforms.PlatformProbeError):
        platforms.probe_databricks(
            ledger_path,
            {
                "DATABRICKS_SERVER_HOSTNAME": "dbc.example.cloud.databricks.com",
                "DATABRICKS_HTTP_PATH": "/sql/warehouse/test",
                "DATABRICKS_TOKEN": "not-a-real-token",
            },
        )
    record = read_records(ledger_path)[0]
    assert record["answer"] == {"status": "failed", "error_type": "TimeoutError"}
    assert record["usage_observations"][0]["amount"] == 0
    assert record["cost_components"][0]["status"] == "unknown"


def test_probe_cli_reports_missing_configuration_without_traceback(
    tmp_path, monkeypatch, capsys
):
    import sys

    from ai_access_cost_experiment.cli import main

    for name in (
        "DATABRICKS_SERVER_HOSTNAME",
        "DATABRICKS_HTTP_PATH",
        "DATABRICKS_CLIENT_ID",
        "DATABRICKS_CLIENT_SECRET",
        "DATABRICKS_TOKEN",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(
        sys,
        "argv",
        ["access-cost", "probe-databricks", "--ledger", str(tmp_path / "runs.jsonl")],
    )
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 2
    assert "Missing Databricks settings" in capsys.readouterr().err