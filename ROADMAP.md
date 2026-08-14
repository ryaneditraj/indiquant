# Roadmap

Living document. Updated after every meaningful iteration.

**Product north star:** Best open-source AI quant research OS for Indian markets (NSE/BSE), extensible to other markets — scientific discovery, not prediction theater.

---

## Phase 0 — Foundation

| Task | Status |
|------|--------|
| Open-source hygiene, monorepo, config contract | ✅ |
| FastAPI + Next.js shells, Docker, CI | ✅ |
| Initial commit | ✅ |

---

## Phase 1 — Research data plane

| Task | Status |
|------|--------|
| Experiment / Hypothesis / Strategy CRUD + SQLite/Postgres | ✅ |
| Data provider plugin interface + registry | ✅ |
| NSE / BSE historical adapters (HTTP + fixture fallback) | ✅ |
| Parquet OHLCV store + Datasets UI | ✅ |
| Corporate actions stub | ✅ |

---

## Phase 2 — Backtest & validation MVP

| Task | Status |
|------|--------|
| Bar engine (fees, slippage, sizing) | ✅ |
| Metrics suite | ✅ |
| Walk-forward, OOS, Monte Carlo, sensitivity, lookahead checks | ✅ |
| Strategy detail page | ✅ |
| Reproducibility score | ✅ |

---

## Phase 3 — AI research loop

| Task | Status |
|------|--------|
| CEO-orchestrated Research → Quant → Backtest → Critic → Risk cycle | ✅ |
| Multi-provider LLM chat (OpenAI-compatible + offline) | ✅ |
| Hypothesis-first generation (no indicator soup) | ✅ |
| Celery task stub for background cycles | ✅ |
| Dashboard live snapshot from DB | ✅ |

---

## Phase 4 — Regimes & stats

| Task | Status |
|------|--------|
| Rule-based regime classifier | ✅ |
| Regime-aware dashboard + API | ✅ |
| Validation suite wired into accept/reject | ✅ |

---

## Phase 5 — Portfolio, search, chat, notebook

| Task | Status |
|------|--------|
| Portfolio correlation / risk contribution / frontier | ✅ |
| Global search (strategies, experiments, hypotheses) | ✅ |
| Project-aware AI chat with experiment citations | ✅ |
| Notebook templates API + UI | ✅ |

---

## Phase 6 — Hardening

| Task | Status |
|------|--------|
| Plugin loader from config module paths | ✅ |
| Audit log + security docs | ✅ |
| SQLite default for local; Postgres via Compose | ✅ |
| CI lint/tests/typecheck | ✅ |

---

## Phase 7 — v0.2 operational depth

| Task | Status |
|------|--------|
| Forever loop pause/resume/stop | ✅ |
| CSV local provider + sample seed | ✅ |
| DuckDB analytics sync/query | ✅ |
| Server notebook execute | ✅ |
| Equity charts + Playwright smoke specs | ✅ |
| Secret encrypt helpers | ✅ |

---

## Next horizon (post-0.2)

| Task | Effort |
|------|--------|
| Live NSE vendor HTTP (contract ready) | L |
| LangGraph durable checkpoints | L |
| Multi-user auth + secrets vault UI | L |
| Options / microstructure plugins | XL |
| Pyodide browser kernel | L |
| CI boots stack + Playwright | M |
| Desktop packaging | L |
| Marketplace package format | M |

---

## Decision log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-07-24 | Monorepo `apps/api` + `apps/web` | Simplicity for OSS |
| 2026-07-24 | Placeholder branding via config | Avoid tight coupling |
| 2026-07-24 | SQLite default + Postgres optional | Zero-friction local research |
| 2026-07-24 | Fixture fallback when NSE URL unset | Reproducible offline demos |
| 2026-07-24 | Hypothesis-first AI cycle | Scientific discovery over indicator soup |
| 2026-07-24 | In-process forever loop + Celery hooks | Pause/resume without Redis required |

---

## How to continue after interruption

1. Read `README.md`, this file, `CHANGELOG.md`, `docs/TODO.md`
2. `make api-test` and open dashboard
3. Pick an item from **Next horizon**. Keep `docs/` free of private sprint logs.
