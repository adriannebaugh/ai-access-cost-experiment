"""Read-only connection probes for optional enterprise platforms."""

import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlsplit

from ai_access_cost_experiment.ledger import append_record


class PlatformConfigurationError(ValueError):
    """Raised when required platform configuration is missing or unsafe."""


class PlatformProbeError(RuntimeError):
    """Raised after a failed probe has been recorded without exposing secrets."""


def probe_databricks(
    ledger_path: Path, env: Mapping[str, str] | None = None
) -> dict[str, Any]:
    settings = os.environ if env is None else env
    config = _databricks_config(settings)
    started = time.perf_counter()
    run_id = str(uuid.uuid4())
    operation_count = 0
    query = "SELECT current_user(), current_catalog(), current_schema()"
    try:
        with _connect_databricks(config) as connection:
            cursor = connection.cursor()
            try:
                operation_count += 1
                cursor.execute(query)
                row = cursor.fetchone()
            finally:
                cursor.close()
        if row is None:
            raise RuntimeError("Probe query returned no row")
        identity = {
            "principal": row[0],
            "catalog": row[1],
            "schema": row[2],
        }
        record = _probe_record(
            run_id=run_id,
            started=started,
            platform="databricks_sql",
            answer=identity,
            operation_count=1,
            governance_notes="read-only identity and session metadata query",
            metadata={"query": query},
        )
    except Exception as error:
        _append_failure(
            ledger_path,
            run_id,
            started,
            "databricks_sql",
            type(error).__name__,
            "read-only identity and session metadata query",
            operation_count=operation_count,
        )
        raise PlatformProbeError(
            f"Databricks probe failed ({type(error).__name__}); see the run ledger."
        ) from None
    append_record(ledger_path, record)
    return record


def probe_salesforce(
    ledger_path: Path, env: Mapping[str, str] | None = None
) -> dict[str, Any]:
    settings = os.environ if env is None else env
    instance_url, access_token = _salesforce_config(settings)
    started = time.perf_counter()
    run_id = str(uuid.uuid4())
    operation_count = 0
    try:
        operation_count += 1
        versions = _salesforce_get(f"{instance_url}/services/data/", access_token)
        version_rows = versions.json()
        if not version_rows:
            raise RuntimeError("Salesforce returned no REST API versions")
        api_version = max(version_rows, key=lambda item: float(item["version"]))["version"]
        operation_count += 1
        limits_response = _salesforce_get(
            f"{instance_url}/services/data/v{api_version}/limits", access_token
        )
        limits = limits_response.json()
        daily_requests = limits.get("DailyApiRequests")
        daily_request_status = None
        if daily_requests:
            daily_request_status = {
                "maximum": daily_requests.get("Max"),
                "remaining": daily_requests.get("Remaining"),
            }
        record = _probe_record(
            run_id=run_id,
            started=started,
            platform="salesforce_rest",
            answer={
                "instance_host": urlsplit(instance_url).hostname,
                "api_version": api_version,
                "daily_api_requests": daily_request_status,
            },
            operation_count=operation_count,
            governance_notes="read-only REST API version and limits requests",
            metadata={"usage_measurements": daily_request_status},
        )
    except Exception as error:
        _append_failure(
            ledger_path,
            run_id,
            started,
            "salesforce_rest",
            type(error).__name__,
            "read-only REST API version and limits requests",
            operation_count=operation_count,
        )
        raise PlatformProbeError(
            f"Salesforce probe failed ({type(error).__name__}); see the run ledger."
        ) from None
    append_record(ledger_path, record)
    return record


def _databricks_config(settings: Mapping[str, str]) -> dict[str, str]:
    required = ("DATABRICKS_SERVER_HOSTNAME", "DATABRICKS_HTTP_PATH")
    missing = [name for name in required if not settings.get(name)]
    if missing:
        raise PlatformConfigurationError(
            "Missing Databricks settings: " + ", ".join(missing)
        )
    client_id = settings.get("DATABRICKS_CLIENT_ID", "")
    client_secret = settings.get("DATABRICKS_CLIENT_SECRET", "")
    token = settings.get("DATABRICKS_TOKEN", "")
    if bool(client_id) != bool(client_secret):
        raise PlatformConfigurationError(
            "Set both DATABRICKS_CLIENT_ID and DATABRICKS_CLIENT_SECRET for OAuth."
        )
    if not client_id and not token:
        raise PlatformConfigurationError(
            "Set a Databricks service-principal OAuth pair or DATABRICKS_TOKEN."
        )
    hostname = settings["DATABRICKS_SERVER_HOSTNAME"].strip()
    parsed_host = urlsplit("//" + hostname)
    if parsed_host.hostname != hostname or parsed_host.port or parsed_host.path:
        raise PlatformConfigurationError(
            "DATABRICKS_SERVER_HOSTNAME must be a hostname, not a URL."
        )
    return {
        "server_hostname": hostname,
        "http_path": settings["DATABRICKS_HTTP_PATH"],
        "client_id": client_id,
        "client_secret": client_secret,
        "access_token": token,
    }


def _salesforce_config(settings: Mapping[str, str]) -> tuple[str, str]:
    instance_url = settings.get("SALESFORCE_INSTANCE_URL", "").rstrip("/")
    access_token = settings.get("SALESFORCE_ACCESS_TOKEN", "")
    if not instance_url or not access_token:
        raise PlatformConfigurationError(
            "Set SALESFORCE_INSTANCE_URL and SALESFORCE_ACCESS_TOKEN."
        )
    parsed = urlsplit(instance_url)
    hostname = parsed.hostname or ""
    valid_domain = hostname.endswith((".salesforce.com", ".force.com"))
    if (
        parsed.scheme != "https"
        or not valid_domain
        or hostname.endswith(".lightning.force.com")
        or parsed.username
        or parsed.password
        or parsed.path
        or parsed.query
        or parsed.fragment
    ):
        raise PlatformConfigurationError(
            "SALESFORCE_INSTANCE_URL must be the HTTPS OAuth instance URL, not a Lightning page URL."
        )
    return instance_url, access_token


def _connect_databricks(config: Mapping[str, str]):
    try:
        from databricks import sql
    except ImportError as error:
        raise RuntimeError(
            "Install optional dependencies with `pip install -e '.[integrations]'`."
        ) from error

    options: dict[str, Any] = {
        "server_hostname": config["server_hostname"],
        "http_path": config["http_path"],
        "user_agent_entry": "ai_access_cost_experiment",
    }
    if config["client_id"]:
        try:
            from databricks.sdk.core import Config, oauth_service_principal
        except ImportError as error:
            raise RuntimeError(
                "Install optional dependencies with `pip install -e '.[integrations]'`."
            ) from error
        sdk_config = Config(
            host=f"https://{config['server_hostname']}",
            client_id=config["client_id"],
            client_secret=config["client_secret"],
        )
        options["credentials_provider"] = lambda: oauth_service_principal(sdk_config)
    else:
        options["access_token"] = config["access_token"]
    return sql.connect(**options)


def _salesforce_get(url: str, access_token: str):
    try:
        import requests
    except ImportError as error:
        raise RuntimeError(
            "Install optional dependencies with `pip install -e '.[integrations]'`."
        ) from error
    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=15,
    )
    response.raise_for_status()
    return response


def _probe_record(
    *,
    run_id: str,
    started: float,
    platform: str,
    answer: Any,
    operation_count: int,
    governance_notes: str,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question_id": "platform_probe",
        "question": f"Verify read-only connectivity to {platform}.",
        "access_path": platform,
        "answer": answer,
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
        "interaction_count": 1,
        "retry_count": 0,
        "correctness": "connectivity_probe",
        "reproducibility": "fixed_read_only_probe",
        "business_context": "not_applicable",
        "governance_notes": governance_notes,
        "usage_observations": [
            {
                "name": "api_or_sql_operations",
                "amount": operation_count,
                "unit": "operation",
                "source": "probe invocation",
                "status": "observed",
            }
        ],
        "metadata": metadata,
        "cost_components": [
            {
                "name": f"{platform}_platform_cost",
                "amount": None,
                "currency": None,
                "unit": "unknown",
                "source": "platform dollar cost not measured by connectivity probe",
                "status": "unknown",
            }
        ],
    }


def _append_failure(
    ledger_path: Path,
    run_id: str,
    started: float,
    platform: str,
    error_type: str,
    governance_notes: str,
    operation_count: int,
) -> None:
    record = _probe_record(
        run_id=run_id,
        started=started,
        platform=platform,
        answer={"status": "failed", "error_type": error_type},
        operation_count=operation_count,
        governance_notes=governance_notes,
        metadata={"probe_status": "failed"},
    )
    append_record(ledger_path, record)