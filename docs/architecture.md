# Architecture

## Purpose

**Pramana** is a research operating system: observe → hypothesize → implement → backtest → validate → reject or improve → document — continuously.

Scientific discovery over prediction theater. *Pramana* = means of valid knowledge.

## Modular surfaces

| Module | Responsibility |
|--------|----------------|
| Web dashboard | Live research cockpit: tasks, experiments, strategies, health |
| API | Auth-ready HTTP, orchestration hooks, persistence |
| Workers | Celery jobs: data ingest, backtests, AI loop steps |
| Data plane | Provider plugins → normalize → Parquet/DuckDB + Postgres metadata |
| Quant core | Strategy IR, event engine, metrics, validation suite |
| AI lab | LangGraph agents (CEO, Research, Quant, Critic, Risk, …) |
| Plugins | Indicators, brokers, charts, models, validators, themes |

## Config precedence

Highest wins for overrides (implementation detail may evolve; document changes here):

1. Process environment / `.env`
2. `settings.json` (machine local)
3. Database / UI settings (runtime)
4. `config.yaml` defaults

Secrets only in env / encrypted store — never in yaml committed to git if they are real credentials. `.env.example` shows names only.

## Data model (core entities)

```
Hypothesis ──▶ Strategy ──▶ Experiment ──▶ ValidationResult
                  │              │
                  │              ├── Metrics
                  │              ├── Trades
                  │              ├── Charts / artifacts
                  │              └── AI notes / rejection reasons
                  └── Versions / evolution history
```

Every experiment has: UUID, timestamps, inputs, outputs, metrics, reasoning, status, tags, reproducibility score, confidence.

## Markets

Primary focus: **India NSE/BSE**.

Market adapters are plugins. Core engine must not assume India-only identifiers forever — isolate exchange calendars, corporate actions, tax/fee defaults behind provider config.

## AI loop (target)

```
CEO
 ├─ Data / Cleaning
 ├─ Research (hypotheses + literature)
 ├─ Quant (strategy code)
 ├─ Backtest
 ├─ Statistician / Critic / Risk
 ├─ Optimizer
 ├─ Portfolio
 └─ Documentation / Security / OSS
```

Agents must cite experiment IDs and never invent metrics.

## Non-goals (near term)

- Live order execution as a product focus
- “Indicator soup” random strategy generators
- Opaque black-box model worship without validation

## Deployment shapes

- Local: Docker Compose + Next + FastAPI
- Cloud: same containers; config-driven
- ARM-compatible images preferred
