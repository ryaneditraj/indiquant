# Architecture

## Purpose

**Indiquant** is Money Radar's research operating system: observe → hypothesize → implement → backtest → validate → reject or improve → document — continuously.

Built by **Thugir Group**. Parent brand: **[Money Radar](https://moneyradar.in)**.

Scientific discovery over prediction theater.

## Modular surfaces

| Module | Responsibility |
|--------|----------------|
| Web dashboard | Live research cockpit |
| API | HTTP, orchestration, persistence |
| Workers | Celery jobs (optional Redis) |
| Data plane | Provider plugins → Parquet/DuckDB |
| Quant core | Backtest, metrics, validation, regimes |
| AI lab | Research loop agents |

## License

PolyForm Noncommercial 1.0.0 — see root `LICENSE`.

## Config precedence

1. Process environment / `.env`
2. `settings.json` (machine local)
3. UI / DB settings (future)
4. `config.yaml` defaults
