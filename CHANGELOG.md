# Changelog

All notable changes to this project are documented here.

Format inspired by [Keep a Changelog](https://keepachangelog.com/).

## [0.2.0] — 2026-07-24

### Added

- Forever research loop with pause / resume / stop (API + AI Lab UI)
- CSV local data provider (`DATA_CSV_ROOT`) + sample seed (`make seed` / `/admin/seed`)
- DuckDB analytics sync + read-only SQL endpoint
- Restricted server notebook execute endpoint + interactive Notebook UI
- Equity curve charts on Experiments
- Secret encrypt/decrypt helpers (Fernet when `ENCRYPTION_KEY` set)
- Playwright smoke specs + `scripts/smoke.sh`
- Celery task wrapper for loop start

### Changed

- Default API version bump to 0.2.0
- Dashboard surfaces live research-loop status

## [0.1.0] — 2026-07-24

### Added

- End-to-end research OS MVP for Indian markets (NSE/BSE-ready adapters)
- Configurable data providers (fixture, NSE HTTP, BSE HTTP) with Parquet store
- Hypothesis / Strategy / Experiment persistence (SQLite default, Postgres via Compose)
- Bar backtest engine with fees/slippage + validation gates
- AI research cycle and offline/LLM chat with experiment citations
- Regime classifier, portfolio lab, global search, audit logs
- Dashboard + functional research surfaces
- Plugin loader driven by `config.yaml` module paths

### Security

- Public settings endpoint never returns raw API keys
- `.env` gitignored; SQLite/local defaults for single-user research

## [Unreleased]

### Added

- N/A
