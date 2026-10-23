# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.5.x   | Security fixes |
| 0.4.x   | Security fixes only |
| older   | Unsupported |

## Reporting a vulnerability

Do **not** open a public GitHub issue for a security bug.

Use a [private security advisory](https://github.com/ryaneditraj/indiquant/security/advisories/new) on `ryaneditraj/indiquant`. Include impact, a reproduction, and the version or commit you tested.

If you cannot use advisories, contact [Ryan Editraj](https://github.com/ryaneditraj) privately. Please allow time for a fix before any public write-up.

## Secrets that belong in the environment

Copy `.env.example` to `.env`. Never commit `.env`, API keys, or provider tokens.

| Name | Purpose |
|------|---------|
| `SECRET_KEY` | Required random value before production or staging |
| `AI_OPENAI_COMPATIBLE_API_KEY` | Optional model provider |
| `AI_LOCAL_API_KEY` | Optional local model |
| `DATA_NSE_API_KEY` / `DATA_BSE_API_KEY` | Optional market-data vendors |
| `ENCRYPTION_KEY` | Optional Fernet material for local helpers |
| `POSTGRES_PASSWORD` | Local Docker Compose only |

Production and staging refuse to boot when `SECRET_KEY` is empty, shorter than 32 characters, or still a documented placeholder.

## What this tree protects

- Symbol, timeframe, and Trends entity ids are restricted before they become filesystem paths
- DuckDB analytics accepts one `SELECT` against registered views and rejects file-reading functions
- Trends CSV cells that look like spreadsheet formulas are prefixed
- Download filenames cannot carry CR, LF, or quotes
- Search treats `%` and `_` as literals
- Notebook execution, sample seeding, and encrypt/decrypt helpers return 403 when `QUANT_OS_ENV` is production or staging
- CORS does not send cookies to a wildcard origin
- The web app sends `X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options`, and a locked-down `Permissions-Policy`

## Known limits

This is a single-operator research OS. It does not have user accounts, and the API trusts whoever can reach it.

- Do not expose port 8000 or the notebook route to the public internet
- `config.yaml` plugin paths are imported and executed. Treat that file as code
- Saved model files under `artifacts/` are loaded with `pickle` and must stay trusted
- The notebook REPL is a convenience for local development, not a sandbox for hostile code
- Docker Compose defaults the local Postgres password to `quant` so `docker compose up` works offline. Change `POSTGRES_PASSWORD` before publishing port 5432
- The API image runs as root so a bind-mounted `./data` directory stays writable. Do not use that image as a multi-tenant host
- Dependency audit on 2026-10-23: Next.js is pinned to 15.5.28, which covers the published App Router advisories fixed in that line. Remaining `npm audit` findings are in Tailwind CSS 3 build tooling (a Tailwind 4 upgrade) and in the PostCSS copy bundled by Next.js 15 (the audit's fix is Next.js 16). Those upgrades change the frontend toolchain and were left in place. Python dependencies were installed at current releases and the test suite passed; no committed third-party API key was found in git history

## Rotate if you ever exposed the local database

The Docker Compose password `quant` (user `quant`, database `quant_os`) has been in the repository since the first commit as a **development default**, not as a cloud credential. If that Postgres port was reachable from anywhere except your machine, change the password and treat the database contents as exposed. No live provider API keys or private keys were found in the git history of this repository.
