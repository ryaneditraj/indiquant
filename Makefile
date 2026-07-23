.PHONY: help up down api-install api-test api-dev web-install web-dev migrate seed smoke

help:
	@echo "Quant OS / Research OS"
	@echo "  make up           - Postgres + Redis"
	@echo "  make down         - Stop compose services"
	@echo "  make api-install  - Install API with dev deps"
	@echo "  make api-test     - Run API pytest"
	@echo "  make api-dev      - Uvicorn reload on :8000"
	@echo "  make web-install  - npm install web"
	@echo "  make web-dev      - Next.js dev on :3000"
	@echo "  make migrate      - Alembic upgrade head"
	@echo "  make seed         - Seed sample CSV + parquet"
	@echo "  make smoke        - curl smoke against :8000"

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
