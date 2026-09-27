"""Append-only JSONL experiment ledger and cost summary."""

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def append_record(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as ledger:
        ledger.write(json.dumps(record, sort_keys=True) + "\n")


def read_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as ledger:
        return [json.loads(line) for line in ledger if line.strip()]


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    totals: dict[tuple[str, str], float] = defaultdict(float)
    observed = estimated = unknown = 0
    for record in records:
        for component in record.get("cost_components", []):
            status = component["status"]
            if status == "observed":
                observed += 1
            elif status == "estimated":
                estimated += 1
            else:
                unknown += 1
            amount = component.get("amount")
            if amount is not None:
                key = (component.get("currency", "UNKNOWN"), component["unit"])
                totals[key] += amount
    return {
        "records": len(records),
        "cost_components": {"observed": observed, "estimated": estimated, "unknown": unknown},
        "totals": [
            {"currency": currency, "unit": unit, "amount": amount}
            for (currency, unit), amount in sorted(totals.items())
        ],
    }