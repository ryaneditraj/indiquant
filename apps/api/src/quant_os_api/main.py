"""FastAPI application entrypoint."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from quant_os_api import __version__
from quant_os_api.config import get_settings
from quant_os_api.db import init_db
from quant_os_api.routes import router


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    init_db()
    settings = get_settings()
    if bool(settings.yaml_config.get("features", {}).get("auto_seed_on_boot", False)):
        from quant_os_api.services import parquet_store
        from quant_os_api.services.seed import seed_sample_data

        if not parquet_store.list_datasets():
            seed_sample_data()
    yield


_OPENAPI_DESCRIPTION = """
**Indiquant** is an open-source AI quantitative research operating system for Indian equity markets (NSE / BSE).

It is a discovery lab, not a trading bot: propose a hypothesis, backtest it, walk-forward validate it, then accept or reject with an experiment ID.

| Area | Prefix |
|------|--------|
| Health / settings | `/api/v1/health`, `/api/v1/settings/public` |
| Research objects | `/api/v1/hypotheses`, `/strategies`, `/experiments` |
| Backtests & validation | `/api/v1/backtests`, `/api/v1/validation` |
| Google Trends intel | `/api/v1/trends` (relative 0–100 index, not volume) |
| AI research loop | `/api/v1/ai` |

Interactive docs: this page. JSON OpenAPI: `/openapi.json`.
"""


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        description=_OPENAPI_DESCRIPTION.strip(),
        version=__version__,
        lifespan=lifespan,
        contact={"name": "Thugir Group", "url": "https://moneyradar.in"},
        license_info={
            "name": "PolyForm Noncommercial 1.0.0",
            "url": "https://polyformproject.org/licenses/noncommercial/1.0.0/",
        },
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router, prefix="/api/v1")

    @app.get("/")
    def root() -> dict[str, str]:
        return {
            "name": settings.app_name,
            "version": __version__,
            "docs": "/docs",
            "health": "/api/v1/health",
        }

    return app


app = create_app()
