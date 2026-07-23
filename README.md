# Quant OS

> Placeholder product name — branding is configurable. Rename via `config.yaml` / Settings UI.

**Open-source AI Quantitative Research Operating System** focused on the Indian equity markets (NSE/BSE), designed to extend to additional markets without redesign.

This is **not** a trading bot, screener, or backtester-as-product.

It is a **research laboratory** whose purpose is to continuously **discover, validate, improve, and organize** trading strategies using AI agents and rigorous statistical methods.

> Every feature must answer: *Does this help discover a real market edge?*

## Principles

| Priority | Meaning |
|----------|---------|
| Simplicity | Prefer clear modules over clever abstractions |
| Modularity | Providers, brokers, models, validators are plugins |
| Reproducibility | Every experiment has UUID, inputs, seeds, metrics |
| Transparency | Rejection reasons, AI notes, and evidence are first-class |
| Configurability | Nothing requires source edits — `.env`, `config.yaml`, Settings UI |
| Evidence | Prefer statistical validation over intuition |

## Architecture (high level)

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Web (Next) │────▶│  API (FastAPI)│────▶│ SQLite/Postgres │
│  Dashboard  │     │  Agents/Jobs  │     │ Parquet store   │
└─────────────┘     └──────┬───────┘     └─────────────────┘
                           │
                    ┌──────▼───────┐
                    │ Redis/Celery │
                    │ Research loop│
                    └──────────────┘
```

See [docs/architecture.md](docs/architecture.md) and [ROADMAP.md](ROADMAP.md).

## Repository layout

```
apps/
  api/          FastAPI research backend
  web/          Next.js dashboard (desktop-first)
config.yaml     Default runtime configuration (no secrets)
.env.example    Secret & environment template
docs/           Architecture, security, TODO
examples/       Curl / workflow examples
```

## Status

**v0.2.0** — Forever loop, DuckDB analytics, CSV provider, notebook execute, equity charts, smoke tests. See [CHANGELOG.md](CHANGELOG.md).

## Quick start (local)

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker optional (Postgres + Redis)

### 1. Configure

```bash
cp .env.example .env
# Default DATABASE_URL is SQLite — no Docker required
```

### 2. API

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn quant_os_api.main:app --reload --port 8000
```

### 3. Web

```bash
cd apps/web
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### 4. First discovery

```bash
curl -X POST http://localhost:8000/api/v1/ai/cycle \
  -H 'Content-Type: application/json' \
  -d '{"symbol":"RELIANCE","provider":"fixture","persist":true}'
```

Optional: `docker compose up -d postgres redis` then point `DATABASE_URL` / `REDIS_URL` at them.

## Configuration

| Layer | Purpose |
|-------|---------|
| `.env` | Secrets, connection strings, API keys |
| `config.yaml` | Non-secret defaults (providers, features, UI name) |
| Settings UI | Runtime public snapshot / future overrides |
| `settings.json` | Optional machine-local overrides |

**Never hardcode** API URLs, keys, providers, brokers, or model names.

## Target users

Retail quants · Professional traders · Researchers · Students · Funds · Universities · AI / financial engineers · Open-source contributors

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Quality bar: tests, docs, reproducibility, no secret commits.

## License

[MIT](LICENSE)
