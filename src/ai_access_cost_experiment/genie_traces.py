"""Synthetic Databricks/Genie interaction traces and cost simulation.

This module generates deterministic synthetic traces of:
- Natural language questions to Genie
- Generated SQL queries
- Query execution metrics (rows scanned, bytes read, duration)
- Databricks compute costs (SQL warehouse usage)
- Genie model inference costs
- Comparison baselines (CLI/direct SQL paths)

Cost estimation follows Databricks public pricing:
- SQL Warehouse: $0.30-0.50/DBU/hour (varies by tier)
- Genie: ~$0.15 per generated query (estimated)
- LLM inference: modeled as additional Genie cost
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

QUESTIONS = [
    "How many available pets have a chaos level above 8?",
    "Show available pets with chaos above 8 and fewer than three applications.",
    "Does chaos appear associated with fewer applications?",
    "Kevin has chaos 10 but gets lots of applications. What makes him an outlier?",
    "Which pets need intervention right now, and why?",
]

GENIE_TRACES = [
    {
        "question_id": "q1",
        "question": "How many available pets have a chaos level above 8?",
        "genie_generated_sql": "SELECT COUNT(*) FROM pets WHERE status = 'Available' AND chaos > 8;",
        "rows_scanned": 15,
        "rows_returned": 1,
        "bytes_read": 540,
        "duration_ms": 245,
        "warehouse_compute_dbu": 0.1,
    },
    {
        "question_id": "q2",
        "question": "Show available pets with chaos above 8 and fewer than three applications.",
        "genie_generated_sql": """
        SELECT p.name FROM pets p
        JOIN applications a ON a.pet_name = p.name
        WHERE p.status = 'Available' AND p.chaos > 8
          AND a.application_count < 3
        ORDER BY p.name;
        """,
        "rows_scanned": 15,
        "rows_returned": 3,
        "bytes_read": 720,
        "duration_ms": 312,
        "warehouse_compute_dbu": 0.12,
    },
    {
        "question_id": "q3",
        "question": "Does chaos appear associated with fewer applications?",
        "genie_generated_sql": """
        SELECT p.chaos, a.application_count FROM pets p
        JOIN applications a ON a.pet_name = p.name
        WHERE p.status = 'Available'
        ORDER BY p.chaos;
        """,
        "rows_scanned": 15,
        "rows_returned": 14,
        "bytes_read": 840,
        "duration_ms": 198,
        "warehouse_compute_dbu": 0.11,
    },
    {
        "question_id": "q4",
        "question": "Kevin has chaos 10 but gets lots of applications. What makes him an outlier?",
        "genie_generated_sql": """
        SELECT p.name, a.application_count, p.good_with_kids, p.species
        FROM pets p
        JOIN applications a ON a.pet_name = p.name
        WHERE p.status = 'Available' AND p.chaos >= 9
        ORDER BY a.application_count DESC;
        """,
        "rows_scanned": 15,
        "rows_returned": 5,
        "bytes_read": 615,
        "duration_ms": 267,
        "warehouse_compute_dbu": 0.11,
    },
    {
        "question_id": "q5",
        "question": "Which pets need intervention right now, and why?",
        "genie_generated_sql": """
        SELECT p.name, p.chaos, p.behavior_risk, a.application_count
        FROM pets p
        JOIN applications a ON a.pet_name = p.name
        WHERE p.status = 'Available'
          AND (p.behavior_risk >= 60 OR (p.chaos >= 9 AND a.application_count <= 2))
        ORDER BY p.name;
        """,
        "rows_scanned": 15,
        "rows_returned": 5,
        "bytes_read": 645,
        "duration_ms": 289,
        "warehouse_compute_dbu": 0.12,
    },
]

CLI_BASELINE_TRACES = [
    {
        "question_id": "q1",
        "question": "How many available pets have a chaos level above 8?",
        "cli_command": "databricks sql execute --query 'SELECT COUNT(*) FROM pets WHERE status = \"Available\" AND chaos > 8;'",
        "rows_scanned": 15,
        "rows_returned": 1,
        "bytes_read": 540,
        "duration_ms": 198,
        "warehouse_compute_dbu": 0.08,
    },
    {
        "question_id": "q2",
        "question": "Show available pets with chaos above 8 and fewer than three applications.",
        "cli_command": "databricks sql execute --query 'SELECT p.name FROM pets p JOIN applications a ON a.pet_name = p.name WHERE p.status = \"Available\" AND p.chaos > 8 AND a.application_count < 3 ORDER BY p.name;'",
        "rows_scanned": 15,
        "rows_returned": 3,
        "bytes_read": 720,
        "duration_ms": 267,
        "warehouse_compute_dbu": 0.10,
    },
    {
        "question_id": "q3",
        "question": "Does chaos appear associated with fewer applications?",
        "cli_command": "databricks sql execute --query 'SELECT p.chaos, a.application_count FROM pets p JOIN applications a ON a.pet_name = p.name WHERE p.status = \"Available\" ORDER BY p.chaos;'",
        "rows_scanned": 15,
        "rows_returned": 14,
        "bytes_read": 840,
        "duration_ms": 156,
        "warehouse_compute_dbu": 0.09,
    },
    {
        "question_id": "q4",
        "question": "Kevin has chaos 10 but gets lots of applications. What makes him an outlier?",
        "cli_command": "databricks sql execute --query 'SELECT p.name, a.application_count, p.good_with_kids, p.species FROM pets p JOIN applications a ON a.pet_name = p.name WHERE p.status = \"Available\" AND p.chaos >= 9 ORDER BY a.application_count DESC;'",
        "rows_scanned": 15,
        "rows_returned": 5,
        "bytes_read": 615,
        "duration_ms": 234,
        "warehouse_compute_dbu": 0.09,
    },
    {
        "question_id": "q5",
        "question": "Which pets need intervention right now, and why?",
        "cli_command": "databricks sql execute --query 'SELECT p.name, p.chaos, p.behavior_risk, a.application_count FROM pets p JOIN applications a ON a.pet_name = p.name WHERE p.status = \"Available\" AND (p.behavior_risk >= 60 OR (p.chaos >= 9 AND a.application_count <= 2)) ORDER BY p.name;'",
        "rows_scanned": 15,
        "rows_returned": 5,
        "bytes_read": 645,
        "duration_ms": 198,
        "warehouse_compute_dbu": 0.10,
    },
]

WAREHOUSE_PRICING = {
    "pro": {"dbu_per_hour": 1.0, "hourly_rate_usd": 0.30},
    "standard": {"dbu_per_hour": 1.0, "hourly_rate_usd": 0.25},
    "classic": {"dbu_per_hour": 1.0, "hourly_rate_usd": 0.40},
}

GENIE_PRICING = {
    "query_generation": 0.15,
    "inference_per_token": 0.00001,
}


def estimate_warehouse_cost(dbu_consumed: float, tier: str = "pro") -> dict[str, Any]:
    """Estimate SQL warehouse cost for a query execution.
    
    Args:
        dbu_consumed: Number of DBUs consumed by the query
        tier: Warehouse tier ('pro', 'standard', 'classic')
    
    Returns:
        Dict with cost estimate, assumptions, and status.
    """
    if tier not in WAREHOUSE_PRICING:
        tier = "pro"
    
    pricing = WAREHOUSE_PRICING[tier]
    cost_usd = dbu_consumed * pricing["hourly_rate_usd"]
    
    return {
        "dbu_consumed": dbu_consumed,
        "warehouse_tier": tier,
        "cost_per_dbu": pricing["hourly_rate_usd"],
        "total_cost_usd": round(cost_usd, 6),
        "status": "estimated",
        "source": "Databricks public pricing",
    }


def estimate_genie_cost(
    tokens_generated: int = 150,
    include_query_generation: bool = True,
) -> dict[str, Any]:
    """Estimate Genie inference and generation cost.
    
    Args:
        tokens_generated: Estimated output tokens from LLM
        include_query_generation: Whether to add query-generation fixed cost
    
    Returns:
        Dict with cost breakdown and assumptions.
    """
    token_cost = tokens_generated * GENIE_PRICING["inference_per_token"]
    query_gen_cost = GENIE_PRICING["query_generation"] if include_query_generation else 0.0
    total = token_cost + query_gen_cost
    
    return {
        "tokens_generated": tokens_generated,
        "token_cost_usd": round(token_cost, 6),
        "query_generation_cost_usd": round(query_gen_cost, 4),
        "total_cost_usd": round(total, 4),
        "status": "estimated",
        "source": "Databricks Genie pricing (estimated)",
    }


def create_genie_trace_record(
    question_idx: int,
    warehouse_tier: str = "pro",
    interaction_count: int = 1,
) -> dict[str, Any]:
    """Create a synthetic Genie interaction trace with costs.
    
    Args:
        question_idx: Index into GENIE_TRACES
        warehouse_tier: SQL warehouse tier for cost estimation
        interaction_count: Number of interactions (retries, refinements)
    
    Returns:
        Complete experiment record with Genie costs.
    """
    trace = GENIE_TRACES[question_idx]
    warehouse_cost = estimate_warehouse_cost(trace["warehouse_compute_dbu"], warehouse_tier)
    genie_cost = estimate_genie_cost()
    
    return {
        "run_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question_id": trace["question_id"],
        "question": trace["question"],
        "access_path": "databricks_genie",
        "genie_generated_sql": trace["genie_generated_sql"].strip(),
        "rows_scanned": trace["rows_scanned"],
        "rows_returned": trace["rows_returned"],
        "bytes_read": trace["bytes_read"],
        "query_duration_ms": trace["duration_ms"],
        "interaction_count": interaction_count,
        "retry_count": 0 if interaction_count == 1 else interaction_count - 1,
        "correctness": "reference_answer",
        "reproducibility": "deterministic_query",
        "business_context": "genie_generated",
        "governance_notes": "SQL generated by Genie; warehouse execution; compute and model costs tracked",
        "cost_components": [
            {
                "name": "sql_warehouse_compute",
                "amount": warehouse_cost["total_cost_usd"],
                "currency": "USD",
                "unit": "query",
                "source": warehouse_cost["source"],
                "status": "estimated",
                "details": warehouse_cost,
            },
            {
                "name": "genie_model_inference",
                "amount": genie_cost["total_cost_usd"],
                "currency": "USD",
                "unit": "query",
                "source": genie_cost["source"],
                "status": "estimated",
                "details": genie_cost,
            },
        ],
    }


def create_cli_trace_record(
    question_idx: int,
    warehouse_tier: str = "pro",
    interaction_count: int = 1,
) -> dict[str, Any]:
    """Create a synthetic CLI baseline trace with costs.
    
    Args:
        question_idx: Index into CLI_BASELINE_TRACES
        warehouse_tier: SQL warehouse tier for cost estimation
        interaction_count: Number of interactions (retries, refinements)
    
    Returns:
        Complete experiment record with CLI baseline costs.
    """
    trace = CLI_BASELINE_TRACES[question_idx]
    warehouse_cost = estimate_warehouse_cost(trace["warehouse_compute_dbu"], warehouse_tier)
    
    return {
        "run_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question_id": trace["question_id"],
        "question": trace["question"],
        "access_path": "databricks_cli",
        "cli_command": trace["cli_command"],
        "rows_scanned": trace["rows_scanned"],
        "rows_returned": trace["rows_returned"],
        "bytes_read": trace["bytes_read"],
        "query_duration_ms": trace["duration_ms"],
        "interaction_count": interaction_count,
        "retry_count": 0 if interaction_count == 1 else interaction_count - 1,
        "correctness": "reference_answer",
        "reproducibility": "deterministic_query",
        "business_context": "human_crafted_sql",
        "governance_notes": "Direct CLI execution; no model inference; warehouse compute tracked",
        "cost_components": [
            {
                "name": "sql_warehouse_compute",
                "amount": warehouse_cost["total_cost_usd"],
                "currency": "USD",
                "unit": "query",
                "source": warehouse_cost["source"],
                "status": "estimated",
                "details": warehouse_cost,
            },
        ],
    }


def generate_genie_vs_cli_traces(
    ledger_path: Path,
    warehouse_tier: str = "pro",
    num_iterations: int = 1,
) -> None:
    """Generate a complete Genie vs. CLI comparison trace to ledger.
    
    Creates paired records for each question: one via Genie, one via CLI.
    """
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    
    with ledger_path.open("a", encoding="utf-8") as ledger:
        for iteration in range(num_iterations):
            for question_idx in range(len(GENIE_TRACES)):
                genie_record = create_genie_trace_record(
                    question_idx,
                    warehouse_tier=warehouse_tier,
                    interaction_count=1,
                )
                ledger.write(json.dumps(genie_record, sort_keys=True) + "\n")
                
                cli_record = create_cli_trace_record(
                    question_idx,
                    warehouse_tier=warehouse_tier,
                    interaction_count=1,
                )
                ledger.write(json.dumps(cli_record, sort_keys=True) + "\n")


def summarize_cost_comparison(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize cost comparison between Genie and CLI paths.
    
    Args:
        records: List of experiment records from ledger
    
    Returns:
        Cost and performance comparison summary.
    """
    genie_records = [r for r in records if r.get("access_path") == "databricks_genie"]
    cli_records = [r for r in records if r.get("access_path") == "databricks_cli"]
    
    def aggregate_costs(path_records):
        total_warehouse = 0.0
        total_genie = 0.0
        total_duration = 0
        
        for record in path_records:
            for component in record.get("cost_components", []):
                if component["name"] == "sql_warehouse_compute":
                    total_warehouse += component.get("amount", 0)
                elif component["name"] == "genie_model_inference":
                    total_genie += component.get("amount", 0)
            total_duration += record.get("query_duration_ms", 0)
        
        return {
            "total_warehouse_cost_usd": round(total_warehouse, 4),
            "total_genie_cost_usd": round(total_genie, 4),
            "total_cost_usd": round(total_warehouse + total_genie, 4),
            "total_duration_ms": total_duration,
            "avg_duration_ms": round(total_duration / len(path_records), 1) if path_records else 0,
        }
    
    genie_summary = aggregate_costs(genie_records)
    cli_summary = aggregate_costs(cli_records)
    
    genie_total = genie_summary["total_cost_usd"]
    cli_total = cli_summary["total_cost_usd"]
    delta = genie_total - cli_total
    delta_pct = ((delta / cli_total) * 100) if cli_total > 0 else 0
    
    return {
        "genie_path": genie_summary,
        "cli_path": cli_summary,
        "comparison": {
            "genie_total_cost_usd": genie_total,
            "cli_total_cost_usd": cli_total,
            "delta_cost_usd": round(delta, 4),
            "delta_percent": round(delta_pct, 1),
            "summary": f"Genie is {abs(delta_pct):.1f}% {'more' if delta > 0 else 'less'} expensive than CLI",
        },
        "record_count": {
            "genie_records": len(genie_records),
            "cli_records": len(cli_records),
        },
    }


__all__ = [
    "QUESTIONS",
    "GENIE_TRACES",
    "CLI_BASELINE_TRACES",
    "WAREHOUSE_PRICING",
    "GENIE_PRICING",
    "estimate_warehouse_cost",
    "estimate_genie_cost",
    "create_genie_trace_record",
    "create_cli_trace_record",
    "generate_genie_vs_cli_traces",
    "summarize_cost_comparison",
]
