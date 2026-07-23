# Roadmap

Living document. Updated after every meaningful iteration.

**Product north star:** Best open-source AI quant research OS for Indian markets (NSE/BSE), extensible to other markets — scientific discovery, not prediction theater.

---

## Phase 0 — Foundation (current)

**Goal:** Recoverable repo, configurable runtime, API + dashboard shells, CI.

| Task | Effort | Status |
|------|--------|--------|
| Open-source hygiene (README, LICENSE, CONTRIBUTING, CHANGELOG) | S | ✅ |
| Monorepo layout (`apps/api`, `apps/web`, `docs`) | S | ✅ |
| Config contract (`.env.example`, `config.yaml`, Pydantic settings) | M | ✅ |
| FastAPI health + settings endpoints + DB models stub | M | ✅ |
| Next.js app shell (nav, dark professional dashboard) | M | ✅ |
| Docker Compose (Postgres, Redis) | S | ✅ |
| GitHub Actions CI smoke | S | ✅ |
| Fixture data provider + plugin protocol | S | ✅ |
| Alembic initial migration (hypotheses/strategies/experiments) | S | ✅ |
| Initial git commit | S | ⬜ (await operator) |

**Exit criteria:** `docker compose up`, API `/health`, web dashboard loads, CI green on PR.

---

## Phase 1 — Research data plane

**Goal:** Persist experiments; ingest modular market data for NSE/BSE.

| Task | Effort | Status |
|------|--------|--------|
| Experiment / Hypothesis / Strategy schemas + Alembic | M | ⬜ |
| Data provider plugin interface | M | ⬜ |
| First NSE historical adapter (configurable) | L | ⬜ |
| Parquet / DuckDB local store for OHLCV | M | ⬜ |
| Datasets UI (list, freshness, schema) | M | ⬜ |
| Corporate actions stub + calendar hooks | M | ⬜ |

**Exit criteria:** Pull Nifty constituents history via config; store experiments with UUID.

---

## Phase 2 — Backtest & validation MVP

**Goal:** Hypothesis → strategy code → backtest → reject/accept with evidence.

| Task | Effort | Status |
|------|--------|--------|
| Event / bar engine (fees, slippage, position sizing) | L | ⬜ |
| Metrics suite (Sharpe, drawdown, turnover, etc.) | M | ⬜ |
| Walk-forward + OOS split | M | ⬜ |
| Lookahead / leakage checks (basic) | M | ⬜ |
| Strategy detail page (idea, logic, metrics, charts) | L | ⬜ |
| Experiment reproducibility score | S | ⬜ |

**Exit criteria:** One documented strategy fully validated end-to-end with rejection path.

---

## Phase 3 — AI research loop

**Goal:** Continuous discovery agents coordinated by CEO agent.

| Task | Effort | Status |
|------|--------|--------|
| LangGraph orchestration skeleton | L | ⬜ |
| Multi-provider LLM config (OpenAI-compatible + local) | M | ⬜ |
| Research → Quant → Backtest → Critic → Risk agents | XL | ⬜ |
| Hypothesis-first generation (no random indicator soup) | L | ⬜ |
| Forever loop worker (Celery) with pause/resume | L | ⬜ |
| Dashboard live AI tasks / queue | M | ⬜ |

**Exit criteria:** Loop invents → tests → documents → rejects/improves without human glue code.

---

## Phase 4 — Statistical depth & regimes

| Task | Effort | Status |
|------|--------|--------|
| Monte Carlo, bootstrap, stress, sensitivity | L | ⬜ |
| Market regime classifier (bull/bear/sideways/vol) | L | ⬜ |
| Regime-conditional strategy performance | M | ⬜ |
| Survivorship bias tooling | M | ⬜ |
| Cross-validation / randomized testing | M | ⬜ |

---

## Phase 5 — Portfolio, notebook, search, chat

| Task | Effort | Status |
|------|--------|--------|
| Portfolio Lab (corr, allocation, frontier) | L | ⬜ |
| In-app notebook + AI assistant | L | ⬜ |
| Global search (strategies, experiments, logs) | M | ⬜ |
| Project-aware AI chat with experiment citations | L | ⬜ |
| Marketplace scaffold (share strategies) | M | ⬜ |

---

## Phase 6 — Hardening & multi-market

| Task | Effort | Status |
|------|--------|--------|
| Plugin registry (indicators, brokers, validators, themes) | L | ⬜ |
| Security (secrets encryption, audit log, permissions) | L | ⬜ |
| Performance (lazy load, cache, streaming large series) | L | ⬜ |
| Multi-market adapter pack (beyond India) | XL | ⬜ |
| Desktop packaging (optional) | L | ⬜ |

---

## Effort key

| Size | Rough meaning |
|------|----------------|
| S | Hours |
| M | 1–3 days |
| L | ~1 week |
| XL | Multi-week |

Estimates assume one focused engineer; parallelize where modules are independent.

---

## Decision log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-07-24 | Monorepo `apps/api` + `apps/web` | Simplicity for OSS; shared config at root |
| 2026-07-24 | Placeholder branding via config | Avoid tight coupling; rename later |
| 2026-07-24 | Postgres + DuckDB/Parquet | OLTP experiments + analytical market data |
| 2026-07-24 | Config layers: env → yaml → settings UI | Nothing hardcoded |

---

## How to continue after interruption

1. Read `README.md`, this file, `CHANGELOG.md`, `docs/TODO.md`
2. Run health checks: API `/health`, web load, `docker compose ps`
3. Pick the next ⬜ / 🔄 item in the current phase
4. Ship tests + docs with the feature; update this roadmap
