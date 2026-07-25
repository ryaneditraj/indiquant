# Indiquant

<p align="center">
  <img src="apps/web/public/brand.svg" width="88" height="88" alt="Indiquant" />
</p>

<h1 align="center">Indiquant</h1>

<p align="center">
  <b>Open-source AI quant research OS for Indian markets (NSE · BSE)</b><br/>
  Hypothesis → backtest → walk-forward proof → accept or reject.<br/>
  Not a trading bot. A discovery lab.
</p>

<p align="center">
  A <a href="https://moneyradar.in"><strong>Money Radar</strong></a> product · Built by <strong>Thugir Group</strong>
</p>

<p align="center">
  <a href="https://github.com/ryaneditraj/indiquant/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/ryaneditraj/indiquant?style=for-the-badge&color=3dff9a&labelColor=030712" /></a>
  <a href="https://github.com/ryaneditraj/indiquant/forks"><img alt="GitHub forks" src="https://img.shields.io/github/forks/ryaneditraj/indiquant?style=for-the-badge&color=22d3ee&labelColor=030712" /></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-PolyForm%20NC-fb7185?style=for-the-badge&labelColor=030712" /></a>
</p>

<p align="center">
  <img alt="NSE" src="https://img.shields.io/badge/NSE-India-3dff9a?style=flat-square&labelColor=030712" />
  <img alt="BSE" src="https://img.shields.io/badge/BSE-India-22d3ee?style=flat-square&labelColor=030712" />
  <img alt="Next.js" src="https://img.shields.io/badge/Next.js-15-white?style=flat-square&labelColor=030712" />
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-Python-009688?style=flat-square&labelColor=030712" />
  <img alt="AI" src="https://img.shields.io/badge/AI-research%20loop-8b9dc3?style=flat-square&labelColor=030712" />
</p>

<p align="center">
  <a href="#quick-start"><b>Quick start</b></a> ·
  <a href="#why-indiquant"><b>Why Indiquant</b></a> ·
  <a href="#features"><b>Features</b></a> ·
  <a href="https://moneyradar.in"><b>Money Radar</b></a>
</p>

---

## Why Indiquant?

Most “AI trading” projects sell vibes. Indiquant sells **evidence**.

| You get | You don’t get |
|--------|----------------|
| Hypothesis-first research loop | Broker auto-trading |
| Walk-forward · Monte Carlo · leakage checks | One cherry-picked equity curve |
| Agents that cite experiment IDs | Opaque “AI picks” |
| Configurable NSE/BSE data providers | Hardcoded vendor lock-in |
| Dashboard-first research OS | CLI-only scripts |

> Every feature must answer: *Does this help discover a real market edge?*

If this saves you from a fake backtest — **[★ star the repo](https://github.com/ryaneditraj/indiquant)** so other Indian quants find it.

---

## Features

- **Forever research loop** — pause / resume / stop AI cycles that propose → test → validate
- **Validation suite** — walk-forward, Monte Carlo, train/test leakage guards
- **Indian market focus** — NSE/BSE providers, Asia/Kolkata defaults, INR research mindset
- **Evidence store** — hypotheses, strategies, experiments with full audit trail
- **Analytics** — Parquet market data + DuckDB queries
- **Dashboard** — dark radar UI, equity charts, live scan status
- **Configurable everything** — `config.yaml` + `.env`, no secret hardcoding
- **Non-commercial OSS** — study & research freely; commercial use needs a license

---

## Stack

```
Next.js + Tailwind  →  FastAPI  →  SQLAlchemy / Parquet / DuckDB
        ↓                    ↓
   Research dashboard    AI agents · backtests · validation
```

---

## Quick start

**Requires:** Python 3.12+ · Node.js 20+

```bash
git clone https://github.com/ryaneditraj/indiquant.git
cd indiquant
cp .env.example .env

# API
cd apps/api && python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
QUANT_OS_CONFIG_PATH=../../config.yaml uvicorn quant_os_api.main:app --reload --port 8000

# Web (new terminal)
cd apps/web && npm install
NEXT_PUBLIC_APP_NAME=Indiquant \
NEXT_PUBLIC_PARENT_BRAND="Money Radar" \
NEXT_PUBLIC_PARENT_URL=https://moneyradar.in \
NEXT_PUBLIC_ORG_NAME="Thugir Group" \
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 \
NEXT_PUBLIC_SITE_URL=https://moneyradar.in/indiquant \
npm run dev
```

Open **http://localhost:3000** → **AI Lab → Start research loop**

```bash
curl -X POST http://localhost:8000/api/v1/ai/cycle \
  -H 'Content-Type: application/json' \
  -d '{"symbol":"RELIANCE","provider":"fixture","persist":true}'
```

Docker: `docker compose up` (see `docker-compose.yml`).

---

## Brand

| Layer | Name |
|-------|------|
| Company | **Thugir Group** |
| Parent | **[Money Radar](https://moneyradar.in)** |
| Product / repo | **Indiquant** → [`ryaneditraj/indiquant`](https://github.com/ryaneditraj/indiquant) |

---

## GitHub topics (paste on repo Settings → Topics)

```
indiquant money-radar nse bse indian-stock-market quant quantitative-finance
algorithmic-trading backtesting walk-forward fastapi nextjs ai-agents
open-source fintech india thugir
```

---

## License — Non-commercial

**[PolyForm Noncommercial License 1.0.0](LICENSE)**

- ✅ Personal research, education, public-interest research
- ❌ Commercial use (paid products, SaaS, commercial trading desks) without a separate license

Commercial licensing: [moneyradar.in](https://moneyradar.in)

---

## Contributing · Security · Roadmap

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SECURITY.md](SECURITY.md)
- [ROADMAP.md](ROADMAP.md)
- [docs/brand.md](docs/brand.md)

---

<p align="center">
  <b>Indiquant</b> · Money Radar · Thugir Group<br/>
  <sub>Scan markets. Prove edges. Never invent evidence.</sub><br/><br/>
  <a href="https://github.com/ryaneditraj/indiquant">★ Star if you’re building Indian market research the honest way</a>
</p>
