# Experiment Repository Guidance

- Keep access paths read-only by default; require an explicit design decision before adding writes.
- Never commit credentials, real customer data, or unverified price assumptions.
- Record measured and estimated costs separately. Missing cost is unknown, not zero.
- Keep each experiment question and access-path result reproducible, timestamped, and append-only.
- Label the local SQLite baseline clearly; do not present it as Databricks usage or pricing.
- Run the focused test suite after changing experiment behavior or ledger schemas.