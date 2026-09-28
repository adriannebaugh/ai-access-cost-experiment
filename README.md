# AI Access Cost Experiment

AI Access Cost Experiment: Genie vs. AI-Assisted CLI using Virtual Pet Adoption Center dataset.

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
4. Compare Databricks Genie One MCP, Databricks SQL MCP, and Salesforce Headless 360 MCP for governed tool access and cross-system reasoning.
5. Use Playwright only for visual verification or evidence capture, not normal data access.

Keep each path's identity, permissions, allowed operations, audit evidence, retries, and human review explicit in run records or accompanying experiment notes.

## Platform Configuration

Install adapters with `python -m pip install -e ".[integrations]"`. Set environment variables from `.env.example` in the terminal or a local untracked environment file; never commit tokens or OAuth secrets.

For Databricks, use `DATABRICKS_SERVER_HOSTNAME` and `DATABRICKS_HTTP_PATH` from the SQL warehouse's connection details. The workspace URL and organization ID do not provide the warehouse HTTP path. Prefer a least-privilege service principal using `DATABRICKS_CLIENT_ID` and `DATABRICKS_CLIENT_SECRET`; a rotated `DATABRICKS_TOKEN` is also supported. The probe runs only `SELECT current_user(), current_catalog(), current_schema()`.

For Salesforce, use `SALESFORCE_INSTANCE_URL` returned by OAuth, not the Lightning browser URL, and a short-lived OAuth access token in `SALESFORCE_ACCESS_TOKEN`. The probe calls only the REST version-discovery and limits endpoints. It records API operations and any daily API request limits returned, but not a dollar price.

Run `access-cost probe-databricks` and `access-cost probe-salesforce` to verify connections. Both append records to the same JSONL ledger. The URLs alone are not authentication, and the initial probe does not query pet/adopter records. Databricks warehouse, Salesforce OAuth setup, source object/table names, and read permissions must be configured before running business questions against live systems. If billing data is unavailable, cost remains unknown; the probes do not infer price from API counts or elapsed time.

## MCP Client Setup

Workspace-level VS Code remote MCP configuration is in `.vscode/mcp.json`. It registers three managed endpoints: Salesforce Headless 360, Databricks Genie One (`system.ai.genie_one_mcp`), and Databricks SQL (`dbsql`). The Databricks workspace currently reports both Databricks services as Active in Unity Gateway.

When VS Code starts a server, it securely prompts for the Salesforce External Client App consumer key and a Databricks personal access token. These values are not stored in the repository. Use a short-lived Databricks token for local testing only, issued to a principal whose Unity Catalog and SQL warehouse grants are limited to the synthetic experiment data. Replace it with an approved OAuth setup for longer-lived or unattended use.

Before starting Salesforce Headless 360, a Salesforce admin must enable the MCP service, create an External Client App, and grant a least-privilege read-only permission set. The VS Code OAuth callback must be allowed by that app. Headless 360 can expose tools capable of writes, so disable mutating tools in VS Code and enforce read-only permissions in Salesforce itself; the client config alone is not a write boundary. The current Salesforce page is not proof that Headless 360 is enabled.

Use **MCP: List Servers** in VS Code to start the endpoints and complete sign-in. Confirm the listed tools and restrict them before using them in a chat. Databricks Genie and SQL MCP usage can incur serverless SQL or SQL warehouse charges. MCP calls are not automatically added to `.experiment/runs.jsonl`; record their run IDs, tool calls, retries, latency, and billing evidence in the experiment ledger. Until a platform meter or bill is captured, leave dollar cost unknown.

## Repository Guidance

See [.github/copilot-instructions.md](.github/copilot-instructions.md) for implementation constraints. No real pet, adopter, or enterprise data belongs in this experiment repository.
