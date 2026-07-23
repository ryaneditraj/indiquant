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
│  Web (Next) │────▶│  API (FastAPI)│────▶│ PostgreSQL      │
│  Dashboard  │     │  Agents/Jobs  │     │ DuckDB / Parquet│
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
packages/       Shared TypeScript / Python packages (growing)
config.yaml     Default runtime configuration (no secrets)
.env.example    Secret & environment template
docs/           Architecture, contribution, design notes
```

## Quick start (local)

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker (recommended for Postgres + Redis)

### 1. Configure

```bash
cp .env.example .env
# Edit .env and config.yaml — never commit secrets
```

### 2. Infrastructure

```bash
docker compose up -d postgres redis
```

### 3. API

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn quant_os_api.main:app --reload --port 8000
```

### 4. Web

```bash
cd apps/web
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Configuration

| Layer | Purpose |
|-------|---------|
| `.env` | Secrets, connection strings, API keys |
| `config.yaml` | Non-secret defaults (providers, features, UI name) |
| Settings UI | Runtime overrides persisted locally / DB |
| `settings.json` | Optional machine-local overrides |

**Never hardcode** API URLs, keys, providers, brokers, or model names.

## Target users

Retail quants · Professional traders · Researchers · Students · Funds · Universities · AI / financial engineers · Open-source contributors

## Status

**Phase 0 — Foundation** in progress. See [ROADMAP.md](ROADMAP.md) and [CHANGELOG.md](CHANGELOG.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Quality bar: tests, docs, reproducibility, no secret commits.

## License

[MIT](LICENSE)
