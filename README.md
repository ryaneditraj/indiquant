<p align="center">
  <img src="apps/web/public/brand.svg" width="88" height="88" alt="Indiquant" />
</p>

<h1 align="center">Indiquant</h1>

<p align="center">
  Open-source AI quant research OS for Indian markets (NSE · BSE) — hypothesis, backtest, walk-forward proof.
</p>

<p align="center">
  <em>Not a trading bot. A discovery lab for NSE/BSE strategy research.</em>
</p>

<p align="center">
  A <a href="https://moneyradar.in"><strong>Money Radar</strong></a> product · Built by <strong>Thugir Group</strong>
</p>

<p align="center">
  <a href="https://github.com/ryaneditraj/indiquant/actions/workflows/ci.yml"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/ryaneditraj/indiquant/ci.yml?branch=main&style=for-the-badge&label=CI&labelColor=030712" /></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-PolyForm%20NC-fb7185?style=for-the-badge&labelColor=030712" /></a>
  <a href="apps/web/package.json"><img alt="Next.js" src="https://img.shields.io/badge/Next.js-15-white?style=for-the-badge&labelColor=030712" /></a>
  <a href="apps/api/pyproject.toml"><img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-Python%203.12-009688?style=for-the-badge&labelColor=030712" /></a>
</p>

<p align="center">
  <img alt="NSE" src="https://img.shields.io/badge/NSE-India-3dff9a?style=flat-square&labelColor=030712" />
  <img alt="BSE" src="https://img.shields.io/badge/BSE-India-22d3ee?style=flat-square&labelColor=030712" />
  <img alt="Google Trends" src="https://img.shields.io/badge/Google%20Trends-intel-fbbf24?style=flat-square&labelColor=030712" />
  <img alt="Walk-forward" src="https://img.shields.io/badge/validation-walk--forward-8b9dc3?style=flat-square&labelColor=030712" />
</p>

---

## Problem

Most “AI trading” tools for the Indian stock market skip the scientific part. They emit a signal, plot one equity curve, and call it research.

If you are looking for an **open-source quant research platform for NSE/BSE** — walk-forward backtesting, leakage checks, experiment IDs, and optional **Google Trends search-demand** as alt-data — that is the gap Indiquant fills.

You still have to reject bad ideas. The OS just makes rejection cheap and documented.

## Why I built this

I wanted a local lab for Indian-market research that treats AI as a hypothesizer, not an oracle. Brokers, vendor APIs, and “alpha” Slack channels are easy to find. A reproducible loop — propose → backtest → walk-forward → accept or reject — was not. Indiquant is that loop, with a dashboard, so the work is inspectable instead of living in a notebook graveyard.

---

## Features

- **Hypothesis-first AI research loop** — pause / resume / stop cycles that propose, test, and cite experiment IDs
- **Validation suite** — walk-forward, Monte Carlo, out-of-sample, lookahead / leakage guards
- **Google Trends intelligence** — multi-entity Search Demand Score (relative 0–100 index, never absolute volume)
- **Indian market defaults** — NSE/BSE providers, Asia/Kolkata, INR backtest assumptions
- **Evidence store** — hypotheses, strategies, experiments, audit log
- **Analytics plane** — Parquet OHLCV + DuckDB `SELECT` queries
- **Radar dashboard** — dark UI, equity charts, Trends ranking, live loop status
- **Config, not hardcoding** — `config.yaml` + `.env`; fixture data so you can demo offline

---

## Screenshot

<p align="center">
  <img src="apps/web/public/og.png" alt="Indiquant research OS — dashboard preview" width="720" />
</p>

<p align="center"><sub>Placeholder: add a short GIF of AI Lab → one cycle → /trends collect after you run <code>make demo</code> locally. Drop it at <code>apps/web/public/demo.gif</code>.</sub></p>

---

## Tech stack

```
Next.js 15 + Tailwind     FastAPI (Python 3.12)
        │                          │
   Research dashboard        Agents · backtests · Trends
                                   │
                    SQLAlchemy · Parquet · DuckDB
                    optional Redis / Celery Beat
```

Interactive API: `http://localhost:8000/docs` after `make api-dev`.

---

## Quick start

**Needs:** Python 3.12+ · Node.js 20+ · ~1 minute if deps are cached. No broker keys required.

```bash
git clone https://github.com/ryaneditraj/indiquant.git
cd indiquant
cp .env.example .env

make api-install && make web-install
make demo                 # sample OHLCV + Trends fixtures
make api-dev              # terminal 1 — http://localhost:8000/docs
make web-dev              # terminal 2 — http://localhost:3000
```

Open **http://localhost:3000** → AI Lab (start the research loop) or **/trends**.

One-shot cycle without the UI:

```bash
curl -X POST http://localhost:8000/api/v1/ai/cycle \
  -H 'Content-Type: application/json' \
  -d '{"symbol":"RELIANCE","provider":"fixture","persist":true}'
```

Docker (Postgres + Redis): `docker compose up`. Full API stack: `docker compose --profile full up`.

`make ci` runs ruff, pytest, and `tsc`.

---

## Architecture

Indiquant is a small monorepo:

| Piece | Role |
|-------|------|
| `apps/web` | Next.js research cockpit |
| `apps/api` | FastAPI: CRUD, backtests, AI loop, Trends |
| `config.yaml` | Non-secret defaults (markets, fees, Trends universe) |
| `.env` | Secrets and URLs — never commit this |
| `data/` | Parquet + SQLite (local) |

Flow: **data plugin → bars → signals → backtest → validation → persist experiment**. The AI loop wraps that with a critic/risk pass. Trends is a parallel intel module (relative search index, confirmatory — not a crystal ball).

Longer write-up: [docs/architecture.md](docs/architecture.md) · Trends: [docs/trends.md](docs/trends.md).

---

## Roadmap

Shipped: research CRUD, fixture NSE/BSE adapters, walk-forward validation, forever AI loop, DuckDB, Google Trends scoring/ranking.

Next (if time): live NSE vendor HTTP, multi-user auth, LangGraph checkpoints, CI that boots the stack + Playwright. See [ROADMAP.md](ROADMAP.md).

---

## License

**[PolyForm Noncommercial License 1.0.0](LICENSE)**

- Personal research, education, public-interest research: yes
- Commercial use (paid products, SaaS, commercial desks): separate license from [Money Radar](https://moneyradar.in)

---

## Docs

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SECURITY.md](SECURITY.md)
- [docs/security.md](docs/security.md)
- [docs/trends.md](docs/trends.md)
- [docs/brand.md](docs/brand.md)

<p align="center">
  <b>Indiquant</b> · Money Radar · Thugir Group<br/>
  <sub>Scan markets. Prove edges. Never invent evidence.</sub>
</p>
