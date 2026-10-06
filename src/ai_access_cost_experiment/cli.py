"""Command line entry point for the offline reference experiment."""

import argparse
import json
import sqlite3
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from ai_access_cost_experiment.dataset import create_database
from ai_access_cost_experiment.ledger import append_record, read_records, summarize
from ai_access_cost_experiment.phase_two import (
    generate_phase_two_dataset,
    summarize_phase_two,
)
from ai_access_cost_experiment.platforms import (
    PlatformConfigurationError,
    PlatformProbeError,
    probe_databricks,
    probe_salesforce,
)
from ai_access_cost_experiment.questions import QUESTIONS, answer_question


def run_local(ledger_path: Path) -> None:
    run_id = str(uuid.uuid4())
    with sqlite3.connect(":memory:") as connection:
        create_database(connection)
        for question_id, question in QUESTIONS:
            started = time.perf_counter()
            answer = answer_question(connection, question_id)
            elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
            record = {
                "run_id": run_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "question_id": question_id,
                "question": question,
                "access_path": "local_sqlite_reference",
                "answer": answer,
                "elapsed_ms": elapsed_ms,
                "interaction_count": 1,
                "retry_count": 0,
                "correctness": "reference_answer",
                "reproducibility": "deterministic_synthetic_data",
                "business_context": "rule_based_or_descriptive_only",
                "governance_notes": "local synthetic data; no external service",
                "cost_components": [
                    {
                        "name": "platform_and_model_cost",
                        "amount": None,
                        "currency": None,
                        "unit": "unknown",
                        "source": "not measured by local baseline",
                        "status": "unknown",
                    }
                ],
            }
            append_record(ledger_path, record)
            print(f"{question_id}: {answer}")
    print(f"Recorded five question results in {ledger_path} (run {run_id}).")


def main() -> None:
    parser = argparse.ArgumentParser(prog="access-cost")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run-local", help="run the offline SQLite reference")
    run_parser.add_argument("--ledger", type=Path, default=Path(".experiment/runs.jsonl"))
    report_parser = subparsers.add_parser("report", help="summarize recorded cost evidence")
    report_parser.add_argument("--ledger", type=Path, default=Path(".experiment/runs.jsonl"))
    databricks_parser = subparsers.add_parser(
        "probe-databricks", help="run a read-only Databricks SQL connection probe"
    )
    databricks_parser.add_argument(
        "--ledger", type=Path, default=Path(".experiment/runs.jsonl")
    )
    salesforce_parser = subparsers.add_parser(
        "probe-salesforce", help="run read-only Salesforce REST API probes"
    )
    salesforce_parser.add_argument(
        "--ledger", type=Path, default=Path(".experiment/runs.jsonl")
    )
    phase_two_parser = subparsers.add_parser(
        "phase-two", help="generate the synthetic Colorado expansion dataset"
    )
    phase_two_parser.add_argument(
        "--output", type=Path, default=Path(".experiment/phase_two.sqlite")
    )
    args = parser.parse_args()

    try:
        if args.command == "run-local":
            run_local(args.ledger)
        elif args.command == "report":
            print(json.dumps(summarize(read_records(args.ledger)), indent=2))
        elif args.command == "probe-databricks":
            record = probe_databricks(args.ledger)
            print(json.dumps(record["answer"], indent=2))
        elif args.command == "probe-salesforce":
            record = probe_salesforce(args.ledger)
            print(json.dumps(record["answer"], indent=2))
        elif args.command == "phase-two":
            output_path = generate_phase_two_dataset(args.output)
            with sqlite3.connect(output_path) as connection:
                summary = summarize_phase_two(connection)
            print(json.dumps(summary, indent=2))
    except (PlatformConfigurationError, PlatformProbeError) as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    main()
