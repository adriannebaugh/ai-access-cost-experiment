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
    generate_national_coverage_dataset,
    summarize_phase_two,
    summarize_national_coverage,
)
from ai_access_cost_experiment.phase_three import (
    generate_phase_three_dataset,
    summarize_phase_three,
    verify_schema_drift_safety,
)
from ai_access_cost_experiment.phase_four import (
    generate_phase_four_dataset,
    summarize_phase_four,
    analyze_shipping_variance,
    analyze_print_failure_costs,
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


def generate_dataset(phase: str, output: Path) -> None:
    """Generate a synthetic dataset for the specified phase."""
    if phase == "two":
        output_path = generate_phase_two_dataset(output)
        with sqlite3.connect(output_path) as connection:
            summary = summarize_phase_two(connection)
        print(f"Phase Two: Colorado expansion (January–December 2026)")
        print(json.dumps(summary, indent=2))
    elif phase == "national":
        output_path = generate_national_coverage_dataset(output)
        with sqlite3.connect(output_path) as connection:
            summary = summarize_national_coverage(connection)
        print(f"Phase Two Extended: National coverage (by EOY 2026)")
        print(json.dumps(summary, indent=2))
    elif phase == "three":
        output_path = generate_phase_three_dataset(output)
        with sqlite3.connect(output_path) as connection:
            summary = summarize_phase_three(connection)
            safety = verify_schema_drift_safety(connection)
        print(f"Phase Three: Extinct species and schema drift (2027)")
        print(f"\nSummary:")
        print(json.dumps(summary, indent=2))
        print(f"\nSchema Drift Safety:")
        print(json.dumps(safety, indent=2))
    elif phase == "four":
        output_path = generate_phase_four_dataset(output)
        with sqlite3.connect(output_path) as connection:
            summary = summarize_phase_four(connection)
            variance = analyze_shipping_variance(connection)
            failures = analyze_print_failure_costs(connection)
        print(f"Phase Four: Designed species and interplanetary (2028–2030)")
        print(f"\nSummary:")
        print(json.dumps(summary, indent=2))
        print(f"\nShipping Variance Analysis:")
        print(json.dumps(variance, indent=2))
        print(f"\nPrint Failure Cost Analysis:")
        print(json.dumps(failures, indent=2))
    else:
        raise ValueError(f"Unknown phase: {phase}")

    print(f"\nDataset written to: {output_path}")


def inspect_dataset(database: Path, phase: str) -> None:
    """Inspect and summarize an existing dataset."""
    if not database.exists():
        raise FileNotFoundError(f"Database not found: {database}")

    with sqlite3.connect(database) as connection:
        if phase == "two":
            summary = summarize_phase_two(connection)
            print(f"Phase Two: Colorado expansion")
            print(json.dumps(summary, indent=2))
        elif phase == "national":
            summary = summarize_national_coverage(connection)
            print(f"Phase Two Extended: National coverage")
            print(json.dumps(summary, indent=2))
        elif phase == "three":
            summary = summarize_phase_three(connection)
            safety = verify_schema_drift_safety(connection)
            print(f"Phase Three: Extinct species and schema drift")
            print(f"\nSummary:")
            print(json.dumps(summary, indent=2))
            print(f"\nSchema Drift Safety Check:")
            print(json.dumps(safety, indent=2))
        elif phase == "four":
            summary = summarize_phase_four(connection)
            variance = analyze_shipping_variance(connection)
            failures = analyze_print_failure_costs(connection)
            print(f"Phase Four: Designed species and interplanetary")
            print(f"\nSummary:")
            print(json.dumps(summary, indent=2))
            print(f"\nShipping Variance Analysis:")
            print(json.dumps(variance, indent=2))
            print(f"\nPrint Failure Cost Analysis:")
            print(json.dumps(failures, indent=2))
        else:
            raise ValueError(f"Unknown phase: {phase}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="access-cost",
        description="AI Access Cost Experiment: compare AI-assisted data access patterns using synthetic datasets.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Legacy command: run-local
    run_parser = subparsers.add_parser("run-local", help="run the offline SQLite reference (legacy)")
    run_parser.add_argument("--ledger", type=Path, default=Path(".experiment/runs.jsonl"))

    # Legacy command: report
    report_parser = subparsers.add_parser("report", help="summarize recorded cost evidence")
    report_parser.add_argument("--ledger", type=Path, default=Path(".experiment/runs.jsonl"))

    # Platform probes
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

    # Dataset generation commands
    generate_parser = subparsers.add_parser(
        "generate",
        help="generate a synthetic dataset for a specific phase",
    )
    generate_parser.add_argument(
        "phase",
        choices=["two", "national", "three", "four"],
        help="phase to generate: two (Colorado), national (50 states), three (extinct species), or four (interplanetary)",
    )
    generate_parser.add_argument(
        "--output",
        type=Path,
        help="output SQLite file path (default: .experiment/phase_{PHASE}.sqlite)",
    )

    # Dataset inspection command
    inspect_parser = subparsers.add_parser(
        "inspect",
        help="inspect and summarize an existing dataset",
    )
    inspect_parser.add_argument(
        "phase",
        choices=["two", "national", "three", "four"],
        help="phase to inspect",
    )
    inspect_parser.add_argument(
        "database",
        type=Path,
        help="SQLite database file to inspect",
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
        elif args.command == "generate":
            output = args.output or Path(f".experiment/phase_{args.phase}.sqlite")
            generate_dataset(args.phase, output)
        elif args.command == "inspect":
            inspect_dataset(args.database, args.phase)
    except (PlatformConfigurationError, PlatformProbeError) as error:
        parser.exit(2, f"error: {error}\n")
    except (FileNotFoundError, ValueError) as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    main()
