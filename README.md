# AI Access Cost Experiment

A headless experiment harness for comparing AI-assisted CLI/SQL with Genie, and later MCP, using a synthetic Virtual Pet Adoption Center dataset. The repository starts with a local SQLite reference path so the question set and cost ledger can be exercised without cloud credentials.

## Quick Start

Requires Python 3.11 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
access-cost run-local
access-cost report
pytest
```

On macOS or Linux, activate with `source .venv/bin/activate`.

`run-local` evaluates the five brief questions against synthetic SQLite data and appends one result per question to `.experiment/runs.jsonl`. Every record includes the shared run ID, timestamp, path, elapsed time, interaction/retry counts, evaluation notes, governance notes, and a cost component. Local execution does not measure platform or model charges, so those costs are recorded as unknown, not zero. The report separates observed, estimated, and unknown components and only totals numeric values.

## Cost Evidence Rules

- Never enter a price unless its source and unit are recorded.
- Mark values `observed` only when captured from a source meter or billing record; mark projections `estimated` and retain the pricing source and assumptions.
- Keep currency and units distinct. Do not sum unlike units or currencies.
- Missing usage, price, or billing data remains unknown.
- Preserve raw JSONL records. Create a new record for corrections instead of silently editing prior experiment evidence.

The local SQLite path is a correctness and workflow reference, not a Databricks cost proxy. `elapsed_ms` is measured locally; all external compute, Genie, and model cost is unknown in this path.

## Experiment Paths

The seeded synthetic dataset and all five question prompts are in `src/ai_access_cost_experiment/`. Question 5 uses an explicit demo rule, `behavior_risk >= 60 OR (chaos >= 9 AND applications <= 2)`, so the result is reproducible rather than a claim that this is the correct shelter policy. Question 3 reports a descriptive Pearson correlation and warns against causal interpretation.

Experiment paths:

1. `probe-databricks` runs a fixed read-only identity/session query through the Databricks SQL Connector.
2. `probe-salesforce` reads REST API versions and API limits; it does not read or modify business records.
3. Run the same prompts through Genie and separately capture Genie-specific usage and underlying compute.
4. Add MCP only to evaluate reusable, governed tool discovery and cross-tool reasoning.
5. Use Playwright only for visual verification or evidence capture, not normal data access.

Keep each path's identity, permissions, allowed operations, audit evidence, retries, and human review explicit in run records or accompanying experiment notes.

## Platform Configuration

Install adapters with `python -m pip install -e ".[integrations]"`. Set environment variables from `.env.example` in the terminal or a local untracked environment file; never commit tokens or OAuth secrets.

For Databricks, use `DATABRICKS_SERVER_HOSTNAME` and `DATABRICKS_HTTP_PATH` from the SQL warehouse's connection details. The workspace URL and organization ID do not provide the warehouse HTTP path. Prefer a least-privilege service principal using `DATABRICKS_CLIENT_ID` and `DATABRICKS_CLIENT_SECRET`; a rotated `DATABRICKS_TOKEN` is also supported. The probe runs only `SELECT current_user(), current_catalog(), current_schema()`.

For Salesforce, use `SALESFORCE_INSTANCE_URL` returned by OAuth, not the Lightning browser URL, and a short-lived OAuth access token in `SALESFORCE_ACCESS_TOKEN`. The probe calls only the REST version-discovery and limits endpoints. It records API operations and any daily API request limits returned, but not a dollar price.

Run `access-cost probe-databricks` and `access-cost probe-salesforce` to verify connections. Both append records to the same JSONL ledger. The URLs alone are not authentication, and the initial probe does not query pet/adopter records. Databricks warehouse, Salesforce OAuth setup, source object/table names, and read permissions must be configured before running business questions against live systems. If billing data is unavailable, cost remains unknown; the probes do not infer price from API counts or elapsed time.

## Repository Guidance

See [.github/copilot-instructions.md](.github/copilot-instructions.md) for implementation constraints. No real pet, adopter, or enterprise data belongs in this experiment repository.