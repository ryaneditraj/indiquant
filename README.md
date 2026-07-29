# Indiquant

<p align="center">
  <img src="apps/web/public/brand.svg" width="88" height="88" alt="Indiquant" />
</p>

<h1 align="center">Indiquant</h1>

<p align="center">
  <b>Open-source AI quant research OS for Indian markets (NSE · BSE)</b><br/>
  Hypothesis → backtest → walk-forward proof → accept or reject.<br/>
  <em>Not a trading bot. A discovery lab.</em>
</p>

<p align="center">
  A <a href="https://moneyradar.in"><strong>Money Radar</strong></a> product · Built by <strong>Thugir Group</strong>
</p>

<p align="center">
  <a href="https://github.com/ryaneditraj/indiquant/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/ryaneditraj/indiquant?style=for-the-badge&color=3dff9a&labelColor=030712" /></a>
  <a href="https://github.com/ryaneditraj/indiquant/network/members"><img alt="GitHub forks" src="https://img.shields.io/github/forks/ryaneditraj/indiquant?style=for-the-badge&color=22d3ee&labelColor=030712" /></a>
  <a href="https://github.com/ryaneditraj/indiquant/actions/workflows/ci.yml"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/ryaneditraj/indiquant/ci.yml?branch=main&style=for-the-badge&label=CI&labelColor=030712" /></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-PolyForm%20NC-fb7185?style=for-the-badge&labelColor=030712" /></a>
</p>

<p align="center">
  <img alt="NSE" src="https://img.shields.io/badge/NSE-India-3dff9a?style=flat-square&labelColor=030712" />
  <img alt="BSE" src="https://img.shields.io/badge/BSE-India-22d3ee?style=flat-square&labelColor=030712" />
  <img alt="Google Trends" src="https://img.shields.io/badge/Google%20Trends-intel-fbbf24?style=flat-square&labelColor=030712" />
  <img alt="Next.js" src="https://img.shields.io/badge/Next.js-15-white?style=flat-square&labelColor=030712" />
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-Python-009688?style=flat-square&labelColor=030712" />
  <img alt="AI" src="https://img.shields.io/badge/AI-research%20loop-8b9dc3?style=flat-square&labelColor=030712" />
</p>

<p align="center">
  <a href="#quick-start"><b>Quick start</b></a> ·
  <a href="#why-indiquant"><b>Why Indiquant</b></a> ·
  <a href="#google-trends-intelligence"><b>Trends</b></a> ·
  <a href="#features"><b>Features</b></a> ·
  <a href="https://moneyradar.in"><b>Money Radar</b></a>
</p>

<p align="center">
  <img src="apps/web/public/og.png" alt="Indiquant — Money Radar research OS preview" width="720" />
</p>

<p align="center"><sub>Radar UI · evidence store · walk-forward validation · Google Trends earnings intel</sub></p>

---

## Why Indiquant?

Most “AI trading” repos sell vibes. Indiquant sells **evidence**.

| You get | You don’t get |
|--------|----------------|
| Hypothesis-first research loop | Broker auto-trading |
| Walk-forward · Monte Carlo · leakage checks | One cherry-picked equity curve |
| Agents that cite experiment IDs | Opaque “AI picks” |
| Google Trends Search Demand Score (relative 0–100) | Fake “absolute volume” claims |
| Configurable NSE/BSE data providers | Hardcoded vendor lock-in |
| Dashboard-first research OS | CLI-only scripts |

> Every feature must answer: *Does this help discover a real market edge?*

No guaranteed returns. No signal theater. Star it if you want Indian market research done the honest way → **[★ ryaneditraj/indiquant](https://github.com/ryaneditraj/indiquant)**

---

## Google Trends intelligence

Retail **search demand** as confirmatory alt-data for Indian consumer names — not a crystal ball.

- Multi-entity universe (DMart, Trent, Blinkit, Zepto, Nykaa, …)
- **Search Demand Score** with quality badges + uncertainty warnings
- Weekly pulls (Celery Beat or `make trends-collect-all`)
- Modeling / ranking / pre-earnings panel / PIT backtest
- Explicit caveat: Trends is a **relative index**, never absolute volume

```bash
make trends-collect ENTITY=dmart   # fixture offline
# then open http://localhost:3000/trends
```

Full module docs: **[docs/trends.md](docs/trends.md)**

---

## Features

- **Forever research loop** — pause / resume / stop AI cycles that propose → test → validate
- **Google Trends intelligence** — multi-entity Search Demand Score + modeling / ranking
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
   Research dashboard    AI agents · backtests · Trends · validation
```

---

## Quick start

**Requires:** Python 3.12+ · Node.js 20+ · under ~60s to first page if deps cached

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

Open **http://localhost:3000** → **AI Lab → Start research loop** · or **`/trends`**

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

See [docs/brand.md](docs/brand.md).

---

## Topics

`indiquant` · `money-radar` · `nse` · `bse` · `indian-stock-market` · `quant` · `quantitative-finance` · `algorithmic-trading` · `backtesting` · `google-trends` · `fastapi` · `nextjs` · `ai-agents` · `fintech` · `india` · `open-source`

---

## License — Non-commercial

**[PolyForm Noncommercial License 1.0.0](LICENSE)**

- ✅ Personal research, education, public-interest research
- ❌ Commercial use (paid products, SaaS, commercial trading desks) without a separate license

Commercial licensing: [moneyradar.in](https://moneyradar.in)

---

## Contributing · Security · Docs

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SECURITY.md](SECURITY.md)
- [docs/trends.md](docs/trends.md) — Google Trends module
- [ROADMAP.md](ROADMAP.md)
- [docs/brand.md](docs/brand.md)

---

<p align="center">
  <b>Indiquant</b> · Money Radar · Thugir Group<br/>
  <sub>Scan markets. Prove edges. Never invent evidence.</sub><br/><br/>
  <a href="https://github.com/ryaneditraj/indiquant">★ Star if you’re building Indian market research the honest way</a>
</p>
