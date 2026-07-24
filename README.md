# Sonar

<p align="center">
  <img src="apps/web/public/brand.svg" width="80" height="80" alt="Sonar mark" />
</p>

<h1 align="center">Sonar</h1>

<p align="center">
  <strong>Evidence-first AI quant research OS</strong> for Indian markets (NSE · BSE)<br/>
  A <a href="https://moneyradar.in"><strong>Money Radar</strong></a> product by <strong>Thugir Group</strong>
</p>

<p align="center">
  <a href="https://moneyradar.in"><img alt="Money Radar" src="https://img.shields.io/badge/parent-Money%20Radar-3dff9a?style=for-the-badge&labelColor=030712" /></a>
  <a href="https://moneyradar.in"><img alt="moneyradar.in" src="https://img.shields.io/badge/web-moneyradar.in-22d3ee?style=for-the-badge&labelColor=030712" /></a>
  <a href="LICENSE"><img alt="Noncommercial" src="https://img.shields.io/badge/license-PolyForm%20Noncommercial-fb7185?style=for-the-badge&labelColor=030712" /></a>
</p>

<p align="center">
  <img alt="NSE" src="https://img.shields.io/badge/NSE-ready-3dff9a?style=flat-square&labelColor=030712" />
  <img alt="BSE" src="https://img.shields.io/badge/BSE-ready-22d3ee?style=flat-square&labelColor=030712" />
  <img alt="AI agents" src="https://img.shields.io/badge/AI-research%20loop-8b9dc3?style=flat-square&labelColor=030712" />
  <img alt="version" src="https://img.shields.io/badge/version-0.4.0-5a6f96?style=flat-square&labelColor=030712" />
</p>

---

### Brand hierarchy

| Layer | Name |
|-------|------|
| Company | **Thugir Group** |
| Parent platform | **[Money Radar](https://moneyradar.in)** (`moneyradar.in`) |
| This product / repo | **Sonar** |

Sonar is the research operating system under Money Radar — continuous discovery of trading strategies with statistical proof, not prediction theater.

> Every feature must answer: *Does this help discover a real market edge?*

## What Sonar is (and is not)

| Sonar | Not Sonar |
|-------|-----------|
| Hypothesis-first research lab | Trading bot / broker |
| Walk-forward · Monte Carlo · leakage checks | One cherry-picked equity curve |
| Agents that cite experiment IDs | Opaque “AI picks” |
| Configurable NSE/BSE providers | Hardcoded vendor lock-in |
| Non-commercial open source | Free-for-commercial SaaS clone |

## SEO / discoverability keywords

Indian stock market research · NSE quant · BSE backtesting · AI trading strategy discovery · walk-forward validation India · open source quant OS · Money Radar Sonar · Thugir Group fintech · reproducible experiments · market regime detection

## Quick start

**Requires:** Python 3.12+, Node.js 20+

```bash
cp .env.example .env

# API
cd apps/api && python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
QUANT_OS_CONFIG_PATH=../../config.yaml uvicorn quant_os_api.main:app --reload --port 8000

# Web
cd apps/web && npm install
NEXT_PUBLIC_APP_NAME=Sonar \
NEXT_PUBLIC_PARENT_BRAND="Money Radar" \
NEXT_PUBLIC_PARENT_URL=https://moneyradar.in \
NEXT_PUBLIC_ORG_NAME="Thugir Group" \
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 \
NEXT_PUBLIC_SITE_URL=https://moneyradar.in/sonar \
npm run dev
```

Open **http://localhost:3000** → **AI Lab → Start research loop**

```bash
curl -X POST http://localhost:8000/api/v1/ai/cycle \
  -H 'Content-Type: application/json' \
  -d '{"symbol":"RELIANCE","provider":"fixture","persist":true}'
```

## License — Non-commercial

Sonar is licensed under the **[PolyForm Noncommercial License 1.0.0](LICENSE)**.

You **may** use, study, modify, and share Sonar for **noncommercial** purposes (personal research, education, public-interest research).

You **may not** use Sonar (or modifications) for **commercial** purposes — including selling access, embedding in paid products, or operating a commercial research/trading service — without a separate commercial license from Thugir Group / Money Radar.

For commercial licensing: **[moneyradar.in](https://moneyradar.in)**

## Stack

Next.js · Tailwind · FastAPI · SQLAlchemy · Parquet · DuckDB · Celery-ready · Pytest · Playwright · GitHub Actions

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Non-commercial license still welcomes community PRs for research and education.

## Security

See [SECURITY.md](SECURITY.md).

## Roadmap

See [ROADMAP.md](ROADMAP.md).

---

<p align="center">
  <sub><strong>Sonar</strong> · Money Radar · Thugir Group<br/>Scan markets. Prove edges. Never invent evidence.</sub>
</p>
