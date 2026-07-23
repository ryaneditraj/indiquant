# Changelog

All notable changes to this project are documented here.

Format inspired by [Keep a Changelog](https://keepachangelog.com/).

## [0.1.0] — 2026-07-24

### Added

- End-to-end research OS MVP for Indian markets (NSE/BSE-ready adapters)
- Configurable data providers (fixture, NSE HTTP, BSE HTTP) with Parquet store
- Hypothesis / Strategy / Experiment persistence (SQLite default, Postgres via Compose)
- Bar backtest engine with fees/slippage + validation gates (walk-forward, Monte Carlo, leakage, sensitivity)
- AI research cycle (CEO-orchestrated) and offline/LLM chat with experiment citations
- Regime classifier, portfolio lab, global search, audit logs, notebook templates
- Dashboard + functional Research, Experiments, Strategies, Datasets, Backtests, AI Lab, Portfolio, Logs pages
- Plugin loader driven solely by `config.yaml` module paths
- Security documentation and append-only audit trail

### Security

- Public settings endpoint never returns raw API keys
- `.env` gitignored; SQLite/local defaults for single-user research

## [Unreleased]

### Added

- N/A
