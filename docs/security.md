# Security

## Secrets

- Never commit `.env`, API keys, or credentials
- Prefer environment variables for secrets; `config.yaml` for non-secret defaults
- Settings UI exposes only `public_info()` (booleans for key presence, never raw keys)

## Audit

- Append-only JSONL audit log at `artifacts/audit/audit.jsonl`
- Research cycles, ingest, and hypothesis creation emit events

## Defaults

- SQLite local default for single-user research
- CORS origins from config
- `SECRET_KEY` must be changed before any multi-user / networked deployment
- Set `QUANT_OS_ENV=production` to disable `/api/v1/security/encrypt` and `/decrypt` (those helpers are for local research only)
- Notebook execute (`POST /api/v1/notebook/execute`) is a restricted local sandbox, not a multi-tenant kernel — do not expose it to untrusted users
- DuckDB analytics accepts a single `SELECT` only; stacked statements are rejected

## Permissions (roadmap hardening)

Role-based access is planned; current single-user local mode trusts the operator.

## Hardening in tree

- Storage ids (`symbol`, `timeframe`, Trends `entity_id`, feature filenames) are allow-listed and must stay inside the configured root
- DuckDB queries cannot call `read_parquet`, `read_csv`, or query a file path directly
- CSV exports neutralize cells that start like spreadsheet formulas
- `POST /api/v1/notebook/execute` and `POST /api/v1/admin/seed` return 403 in production and staging
- Startup refuses a placeholder `SECRET_KEY` in those environments
- Repo-root `.env` is loaded even when Uvicorn is started from `apps/api`

See [SECURITY.md](../SECURITY.md) for reporting and the limits that are still open.
