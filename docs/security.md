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

## Permissions (roadmap hardening)

Role-based access is planned; current single-user local mode trusts the operator.
