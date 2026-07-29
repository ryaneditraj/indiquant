"""Celery app — research loop worker (optional Redis)."""

from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from quant_os_api.config import get_settings

settings = get_settings()
celery_app = Celery(
    "quant_os",
    broker=settings.broker_url,
    backend=settings.result_backend,
)
_celery_yaml = settings.yaml_config.get("celery", {}) or {}
celery_app.conf.task_always_eager = bool(_celery_yaml.get("task_always_eager", False))

# Weekly Trends collect — Sunday 02:30 Asia/Kolkata
_tz = str(
    (settings.yaml_config.get("google_trends") or {}).get("timezone")
    or (settings.yaml_config.get("app") or {}).get("default_timezone")
    or "Asia/Kolkata"
)
celery_app.conf.timezone = _tz
celery_app.conf.enable_utc = False
celery_app.conf.beat_schedule = {
    "trends-weekly-collect": {
        "task": "quant_os.trends_collect_all",
        "schedule": crontab(minute=30, hour=2, day_of_week="sun"),
        "options": {"expires": 3600},
    },
}


@celery_app.task(name="quant_os.research_cycle")
def research_cycle_task(symbol: str = "RELIANCE", seed: int = 42) -> dict:
    from quant_os_api.services.ai_loop import run_research_cycle

    result = run_research_cycle(symbol=symbol, seed=seed)
    return {
        "run_id": result.run_id,
        "accepted": result.accepted,
        "experiment_id": result.experiment["id"],
    }


@celery_app.task(name="quant_os.trends_collect")
def trends_collect_task(entity_id: str = "dmart", provider: str | None = None) -> dict:
    """Weekly/daily Trends pull — relative indices only, not absolute volume."""
    from quant_os_api.trends.collector import collect_entity
    from quant_os_api.trends.score import score_entity

    collected = collect_entity(entity_id, provider=provider)
    scored = score_entity(entity_id)
    return {
        "run_id": collected.get("run_id"),
        "entity_id": entity_id,
        "interest_rows": collected.get("interest_rows"),
        "search_demand_score": scored.get("search_demand_score"),
        "quality_badge": scored.get("quality_badge"),
        "is_absolute_volume": False,
    }


@celery_app.task(name="quant_os.trends_collect_all")
def trends_collect_all_task(provider: str | None = None) -> dict:
    """Beat entrypoint — collect + score every configured Trends entity."""
    from quant_os_api.trends.universe import list_entities

    results = []
    for eid in list_entities():
        try:
            results.append(trends_collect_task(eid, provider=provider))
        except Exception as exc:  # noqa: BLE001
            results.append({"entity_id": eid, "ok": False, "error": str(exc)})
    return {
        "ok": True,
        "n": len(results),
        "results": results,
        "is_absolute_volume": False,
    }
