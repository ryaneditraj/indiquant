# Google Trends Intelligence Module

Evidence-first retail search demand layer for **Indiquant** (Money Radar · Thugir Group).

Phase 1 (DMart) + Phase 2 multi-entity framework + modeling layer. Confirmatory alt-data only — never a standalone trade signal.

## Non-negotiable

- Trends is a **relative 0–100 index** within selected time + geography — **not absolute volume**.
- Terms in the **same request** are normalized relative to each other — preserve `query_group` context.
- Never compare separate exports without **anchors** or shared comparison windows.
- Region maps and related/rising queries are **independent signal channels**.
- Always expose **uncertainty / sparse-data** warnings and **quality badges**.
- Confirmatory alt-data only — combine with satellite, app, pricing, hiring.

## Phase status

| Piece | Status |
|-------|--------|
| DMart + Phase 2 entities (Trent, Reliance Smart, JioMart, BigBasket, Blinkit, Zepto, Nykaa, Titan) | ✅ `config.yaml` |
| Fixture collector + optional `pytrends` | ✅ |
| Weekly automation (Celery Beat + Makefile/cron script) | ✅ |
| Raw PIT parquet + run manifests | ✅ `data/parquet/trends/` |
| Feature engineering (incl. QoQ/YoY/festival/cross-signal/confirmation) | ✅ |
| Search Demand Score + alerts + pre-earnings + PIT backtest | ✅ |
| Cross-signal fixture adapters (satellite / app / pricing / hiring) | ✅ |
| GB modeling (rev / SSS / beat-miss / nowcast / ranking) + conformal bands | ✅ `artifacts/trends/` |
| Export JSON + CSV | ✅ `?format=json|csv` |
| `/trends` multi-entity UI + ranking | ✅ |

## Weekly automated pulls

**Celery Beat** (wired in `quant_os_api.workers`):

- Schedule: Sunday **02:30** `Asia/Kolkata`
- Task: `quant_os.trends_collect_all` → per-entity `quant_os.trends_collect`

```bash
# Worker + Beat (requires Redis)
celery -A quant_os_api.workers.celery_app worker -l info
celery -A quant_os_api.workers.celery_app beat -l info
```

**Cron / Makefile** (no Redis required — fixture or pytrends):

```bash
make trends-collect ENTITY=dmart
make trends-demo                 # dmart + trent fixture collect + rank
make demo                        # sample OHLCV seed + trends-demo
make trends-collect-all          # scripts/trends_weekly.sh
# crontab example:
# 30 2 * * 0 cd /path/to/quant-os && bash scripts/trends_weekly.sh >> logs/trends_cron.log 2>&1
```

Empty `/trends` after clone is expected — run `make trends-demo`, then Refresh. Ranking `side_hint` is a relative tertile label (`long` / `neutral` / `short` / `watch`); unreliable quality → `watch`. Not trade advice.

## API

```bash
# List entities
curl localhost:8000/api/v1/trends/entities

# Collect (fixture offline)
curl -X POST localhost:8000/api/v1/trends/collect \
  -H 'Content-Type: application/json' \
  -d '{"entity_id":"dmart","provider":"fixture"}'

# Collect all Phase 2 names
curl -X POST localhost:8000/api/v1/trends/collect-all

# Dashboard / score / export
curl localhost:8000/api/v1/trends/trent/dashboard
curl -X POST localhost:8000/api/v1/trends/score \
  -H 'Content-Type: application/json' \
  -d '{"entity_id":"blinkit","window":"90d"}'
curl localhost:8000/api/v1/trends/dmart/export > dmart-trends.json
curl localhost:8000/api/v1/trends/dmart/export?format=csv > dmart-trends.csv
# CSV is relative index rows only — never absolute volume

# Modeling (proxy labels until fundamentals wired; label_source in train meta)
curl -X POST localhost:8000/api/v1/trends/models/train -H 'Content-Type: application/json' -d '{}'
curl localhost:8000/api/v1/trends/dmart/predict
curl localhost:8000/api/v1/trends/dmart/nowcast
curl localhost:8000/api/v1/trends/comparison
curl localhost:8000/api/v1/trends/comparison?format=csv > trends-comparison.csv
# Empty rankings → header-only CSV (soft success)

# PIT pre-earnings backtest
curl -X POST localhost:8000/api/v1/trends/dmart/backtest
```

## Weekly Beat smoke

```bash
make trends-beat-smoke   # prints trends-weekly-collect → Sunday 02:30 Asia/Kolkata
# or: pytest apps/api/tests/test_celery_beat.py -q
```

## Live pulls

```bash
pip install 'quant-os-api[trends]'   # pytrends
# config: google_trends.default_provider: pytrends
# optional: pytrends_retries / pytrends_backoff_sec / pytrends_request_gap_sec
```

Live collector uses request gaps + exponential backoff on 429s; on hard failure it falls back to fixture with `live_error` set.

## Score subcomponents

1. Brand attention  
2. Purchase intent  
3. Regional strength  
4. Competitive share  
5. Risk / friction  
6. Signal quality / confidence  

## Modeling notes

Targets are **synthetic proxies** (score regime + noise) until filings / SSS / beat-miss labels are wired via `trends/fundamentals.py` (`load_labels` stub → `None`; train meta exposes `label_source`). Artifacts: `artifacts/trends/models.pkl`, `train_meta.json`. Predictions include heuristic conformal residual bands because Trends is sampled and noisy.

## Phase 2 entities

| ID | Label | Notes |
|----|-------|-------|
| `dmart` | DMart | Phase 1 reference |
| `trent` | Trent | Westside / Zudio |
| `reliance_smart` | Reliance Smart | Reliance Retail grocery proxy |
| `jiomart` | JioMart | Reliance Retail online proxy |
| `bigbasket` | BigBasket | Tata Digital / bbnow |
| `blinkit` | Blinkit | Quick commerce |
| `zepto` | Zepto | Quick commerce |
| `nykaa` | Nykaa | Beauty / consumer |
| `titan` | Titan | Tanishq / watches |
