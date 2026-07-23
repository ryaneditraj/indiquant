"""HTTP routers."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from quant_os_api import __version__
from quant_os_api.config import get_settings
from quant_os_api.schemas import DashboardSnapshot, HealthResponse, SettingsPublicResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    info = settings.public_info()
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version=__version__,
        env=settings.quant_os_env,
        primary_market=str(info.get("primary_market", "IN")),
        database_configured=bool(settings.database_url),
        redis_configured=bool(settings.redis_url),
        features=dict(info.get("features") or {}),
    )


@router.get("/settings/public", response_model=SettingsPublicResponse)
def public_settings() -> SettingsPublicResponse:
    return SettingsPublicResponse(settings=get_settings().public_info())


@router.get("/dashboard/snapshot", response_model=DashboardSnapshot)
def dashboard_snapshot() -> DashboardSnapshot:
    settings = get_settings()
    return DashboardSnapshot(
        app_name=settings.app_name,
        research_score=0.0,
        ai_tasks=[
            {
                "id": "bootstrap",
                "agent": "ceo",
                "title": "Foundation online — awaiting research loop enable",
                "status": "idle",
            }
        ],
        queued_experiments=0,
        completed_experiments=0,
        rejected_strategies=0,
        top_strategies=[],
        market_regime="unclassified",
        data_freshness="no-providers-connected",
        system_health={
            "api": "ok",
            "workers": "not-started",
            "database": "configured" if settings.database_url else "missing",
            "redis": "configured" if settings.redis_url else "missing",
        },
        recent_discoveries=[],
        timeline=[
            {
                "ts": "phase-0",
                "event": "Repository foundation scaffolded",
                "detail": "Config contract, API health, dashboard shell",
            }
        ],
    )


@router.get("/meta/nav")
def navigation() -> dict[str, Any]:
    """Single source of truth for app sections — keeps branding/config soft."""
    settings = get_settings()
    features = settings.yaml_config.get("features", {})
    sections = [
        {"id": "dashboard", "label": "Dashboard", "href": "/"},
        {"id": "research", "label": "Research", "href": "/research"},
        {"id": "experiments", "label": "Experiments", "href": "/experiments"},
        {"id": "strategies", "label": "Strategies", "href": "/strategies"},
        {"id": "datasets", "label": "Datasets", "href": "/datasets"},
        {"id": "backtests", "label": "Backtests", "href": "/backtests"},
        {"id": "validation", "label": "Validation", "href": "/validation"},
        {"id": "optimization", "label": "Optimization", "href": "/optimization"},
        {"id": "portfolio", "label": "Portfolio", "href": "/portfolio"},
        {"id": "ai-lab", "label": "AI Lab", "href": "/ai-lab"},
        {
            "id": "notebook",
            "label": "Notebook",
            "href": "/notebook",
            "enabled": bool(features.get("notebook_enabled", False)),
        },
        {"id": "logs", "label": "Logs", "href": "/logs"},
        {
            "id": "marketplace",
            "label": "Marketplace",
            "href": "/marketplace",
            "enabled": bool(features.get("marketplace_enabled", False)),
        },
        {"id": "settings", "label": "Settings", "href": "/settings"},
        {"id": "docs", "label": "Documentation", "href": "/docs"},
    ]
    return {"app_name": settings.app_name, "sections": sections}
