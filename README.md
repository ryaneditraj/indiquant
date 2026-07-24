# Pramana

<p align="center">
  <img src="apps/web/public/brand.svg" width="72" height="72" alt="Pramana mark" />
</p>

<h1 align="center">Pramana</h1>

<p align="center">
  <strong>Evidence-first AI quant research OS</strong> for Indian markets (NSE/BSE)
</p>

<p align="center">
  <a href="#quick-start"><img alt="Quick start" src="https://img.shields.io/badge/quick%20start-2%20commands-c8f54a?style=flat-square&labelColor=06110d" /></a>
  <a href="LICENSE"><img alt="MIT" src="https://img.shields.io/badge/license-MIT-4fd1c5?style=flat-square&labelColor=06110d" /></a>
  <a href="CHANGELOG.md"><img alt="version" src="https://img.shields.io/badge/version-0.3.0-8fb29e?style=flat-square&labelColor=06110d" /></a>
  <a href="#philosophy"><img alt="not a bot" src="https://img.shields.io/badge/not%20a-trading%20bot-fb7185?style=flat-square&labelColor=06110d" /></a>
</p>

---

**Pramana** (प्रमाण) means *a means of valid knowledge* — proof, evidence, warrant.

This project is an open-source **research laboratory** that continuously **discovers, validates, improves, and organizes** trading strategies using AI agents and rigorous statistics.

It is **not** a trading bot.  
It is **not** another screener.  
It is **not** prediction theater.

> Every feature must answer: *Does this help discover a real market edge?*

## Why Pramana

| Most quant tools | Pramana |
|------------------|---------|
| Combine indicators and hope | Hypotheses first, then code |
| One pretty backtest | Walk-forward, Monte Carlo, leakage checks |
| Opaque “AI picks” | Agents cite experiment IDs — or stay offline |
| Hardcoded vendors | Every provider/URL/key is configurable |
| Lose the trail | Every rejection reason is stored |

## Screenshot of the cockpit

Run locally and open [http://localhost:3000](http://localhost:3000) — dark forest UI, lime edge accents, live loop status, searchable experiments.

```
Dashboard → Research / AI Lab → Experiments (equity curves) → Strategies
```

## Quick start

**Prerequisites:** Python 3.12+, Node.js 20+

```bash
cp .env.example .env

# API
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
QUANT_OS_CONFIG_PATH=../../config.yaml uvicorn quant_os_api.main:app --reload --port 8000

# Web (new terminal)
cd apps/web
npm install
NEXT_PUBLIC_APP_NAME=Pramana NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

Then:

1. Open **http://localhost:3000**
2. Go to **AI Lab → Start research loop**
3. Watch accept / reject land in **Experiments**

Or one-shot:

```bash
curl -X POST http://localhost:8000/api/v1/ai/cycle \
  -H 'Content-Type: application/json' \
  -d '{"symbol":"RELIANCE","provider":"fixture","persist":true}'
```

## Philosophy

1. **Simplicity** — clear modules over clever abstractions  
2. **Modularity** — providers, brokers, models, validators as plugins  
3. **Reproducibility** — UUID, inputs, seeds, metrics on every experiment  
4. **Transparency** — rejection reasons are first-class  
5. **Configurability** — `.env` + `config.yaml` + Settings UI; no source edits  
6. **Evidence** — statistical validation over intuition  

## Architecture

```
┌──────────────┐     ┌────────────────┐     ┌──────────────────┐
│  Web (Next)  │────▶│  API (FastAPI)  │────▶│ SQLite / Postgres│
│  Pramana UI  │     │  Agents / Loop  │     │ Parquet + DuckDB │
└──────────────┘     └────────┬───────┘     └──────────────────┘
                              │
                       ┌──────▼───────┐
                       │ Redis/Celery │  (optional)
                       └──────────────┘
```

## Repository layout

```
apps/api/       FastAPI research backend
apps/web/       Next.js desktop-first dashboard
config.yaml     Non-secret defaults (rename branding here)
.env.example    Secrets template
docs/           Architecture, security, brand
examples/       Curl workflows
scripts/        Smoke checks
```

## Configuration

Nothing requires a code edit to swap vendors:

| Layer | Purpose |
|-------|---------|
| `.env` | Secrets, `DATABASE_URL`, AI keys, `DATA_*_URL` |
| `config.yaml` | App name, feature flags, plugin module paths |
| Settings UI | Public runtime snapshot |

Point `DATA_NSE_API_BASE_URL` at your vendor when ready — until then, fixture / CSV mode stays reproducible offline.

## Stack

Next.js · Tailwind · FastAPI · SQLAlchemy · Parquet · DuckDB · Celery-ready · Pytest · Playwright · GitHub Actions

## Contributing

We welcome researchers, engineers, and students.

- Read [CONTRIBUTING.md](CONTRIBUTING.md)
- Follow the edge test: *does this help discover a real edge?*
- Never commit secrets
- Update `CHANGELOG.md` for user-facing changes

## Security

See [docs/security.md](docs/security.md) and [SECURITY.md](SECURITY.md).

## Roadmap

See [ROADMAP.md](ROADMAP.md). Near-term: real NSE vendor adapters, durable agent graphs, multi-user auth.

## License

[MIT](LICENSE) — use it, fork it, teach with it, fund research with it.

---

<p align="center"><sub>Pramana — proof before prediction.</sub></p>
