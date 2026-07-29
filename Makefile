.PHONY: help up down api-install api-test api-dev web-install web-dev migrate seed smoke trends-collect trends-collect-all trends-train trends-demo demo

help:
	@echo "Indiquant · Money Radar · Thugir Group"
	@echo "  make up               - Postgres + Redis"
	@echo "  make down             - Stop compose services"
	@echo "  make api-install      - Install API with dev deps"
	@echo "  make api-test         - Run API pytest"
	@echo "  make api-dev          - Uvicorn reload on :8000"
	@echo "  make web-install      - npm install web"
	@echo "  make web-dev          - Next.js dev on :3000"
	@echo "  make migrate          - Alembic upgrade head"
	@echo "  make seed             - Seed sample CSV + parquet (OHLCV)"
	@echo "  make trends-demo      - Fixture Trends collect for dmart + trent"
	@echo "  make demo             - seed + trends-demo (offline star-path)"
	@echo "  make smoke            - curl smoke against :8000"
	@echo "  make trends-collect ENTITY=dmart - Fixture Trends pull + score"
	@echo "  make trends-collect-all - All configured Trends entities"
	@echo "  make trends-train     - Train Trends GB models (proxy labels)"

up:
	docker compose up -d postgres redis

down:
	docker compose down

api-install:
	cd apps/api && python3 -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"

api-test:
	cd apps/api && . .venv/bin/activate && QUANT_OS_CONFIG_PATH=../../config.yaml pytest -q

api-dev:
	cd apps/api && . .venv/bin/activate && QUANT_OS_CONFIG_PATH=../../config.yaml uvicorn quant_os_api.main:app --reload --port 8000

web-install:
	cd apps/web && npm install

web-dev:
	cd apps/web && npm run dev

migrate:
	cd apps/api && . .venv/bin/activate && QUANT_OS_CONFIG_PATH=../../config.yaml alembic upgrade head

seed:
	cd apps/api && . .venv/bin/activate && QUANT_OS_CONFIG_PATH=../../config.yaml python -c "from quant_os_api.services.seed import seed_sample_data; print(seed_sample_data())"

smoke:
	bash scripts/smoke.sh

trends-collect:
	cd apps/api && . .venv/bin/activate && QUANT_OS_CONFIG_PATH=../../config.yaml python -c "from quant_os_api.trends.collector import collect_entity; from quant_os_api.trends.score import score_entity; e='$(or $(ENTITY),dmart)'; c=collect_entity(e, provider='fixture'); s=score_entity(e); print({'entity':e,'run':c.get('run_id'),'score':s.get('search_demand_score'),'badge':s.get('quality_badge'),'is_absolute_volume':False})"

trends-collect-all:
	bash scripts/trends_weekly.sh

trends-train:
	cd apps/api && . .venv/bin/activate && QUANT_OS_CONFIG_PATH=../../config.yaml python -c "from quant_os_api.trends.modeling import train_models; print(train_models())"

trends-demo:
	@echo "→ Fixture Trends demo (dmart + trent) — relative index, never absolute volume"
	bash scripts/trends_demo.sh

demo: seed trends-demo
	@echo ""
	@echo "Demo data ready."
	@echo "  1. make api-dev     # :8000"
	@echo "  2. make web-dev     # :3000"
	@echo "  3. Open /trends and AI Lab — fixture only, no live keys required"
