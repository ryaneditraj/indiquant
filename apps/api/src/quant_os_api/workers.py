"""Celery app — research loop worker (optional Redis)."""

from __future__ import annotations

from celery import Celery

from quant_os_api.config import get_settings

settings = get_settings()
celery_app = Celery(
    "quant_os",
    broker=settings.broker_url,
    backend=settings.result_backend,
)
celery_app.conf.task_always_eager = bool(
    settings.yaml_config.get("celery", {}).get("task_always_eager", False)
)


@celery_app.task(name="quant_os.research_cycle")
def research_cycle_task(symbol: str = "RELIANCE", seed: int = 42) -> dict:
    from quant_os_api.services.ai_loop import run_research_cycle

    result = run_research_cycle(symbol=symbol, seed=seed)
    return {
        "run_id": result.run_id,
        "accepted": result.accepted,
        "experiment_id": result.experiment["id"],
    }


@celery_app.task(name="quant_os.research_loop_start")
def research_loop_start_task(
    symbols: list[str] | None = None,
    max_cycles: int = 5,
    provider: str = "fixture",
) -> dict:
    from quant_os_api.services.research_loop import get_loop_controller

    return get_loop_controller().start(
        symbols=symbols,
        provider=provider,
        max_cycles=max_cycles,
    )
