"""HTTP routers — research OS API surface."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any
from uuid import UUID, uuid4

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from quant_os_api import __version__
from quant_os_api.config import get_settings
from quant_os_api.db import get_db
from quant_os_api.models import Experiment, Hypothesis, Strategy
from quant_os_api.plugins.registry import get_registry
from quant_os_api.quant.backtest import (
    BacktestConfig,
    mean_reversion_signals,
    sma_crossover_signals,
)
from quant_os_api.quant.regimes import classify_regimes, current_regime
from quant_os_api.quant.validation import validate_strategy
from quant_os_api.schemas import (
    BacktestRequest,
    ChatRequest,
    DashboardSnapshot,
    DuckDBQueryRequest,
    EncryptRequest,
    ExperimentCreate,
    ExperimentOut,
    HealthResponse,
    HypothesisCreate,
    HypothesisOut,
    IngestRequest,
    LoopControlRequest,
    NotebookExecuteRequest,
    PortfolioRequest,
    ResearchCycleRequest,
    SettingsPublicResponse,
    StrategyCreate,
    StrategyOut,
    TrendsCollectRequest,
    TrendsPredictRequest,
    TrendsRankRequest,
    TrendsScoreRequest,
    TrendsTrainRequest,
)
from quant_os_api.services import parquet_store
from quant_os_api.services.ai_loop import llm_chat, run_research_cycle
from quant_os_api.services.audit import read_audit, write_audit
from quant_os_api.services.duckdb_store import query_duckdb, sync_parquet_to_duckdb
from quant_os_api.services.notebook import execute_notebook_code
from quant_os_api.services.persistence import persist_loop_result
from quant_os_api.services.portfolio import portfolio_report
from quant_os_api.services.research_loop import get_loop_controller
from quant_os_api.services.secrets import decrypt_secret, encrypt_secret
from quant_os_api.services.seed import seed_sample_data

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
def dashboard_snapshot(db: Session = Depends(get_db)) -> DashboardSnapshot:
    settings = get_settings()
    experiments = list(db.scalars(select(Experiment).order_by(Experiment.created_at.desc()).limit(50)))
    strategies = list(db.scalars(select(Strategy).order_by(Strategy.created_at.desc()).limit(10)))
    completed = sum(1 for e in experiments if e.status in {"completed", "accepted"})
    rejected = sum(1 for e in experiments if e.status == "rejected")
    queued = sum(1 for e in experiments if e.status == "queued")
    accepted = sum(1 for e in experiments if e.status == "accepted")
    score = (accepted / len(experiments)) if experiments else 0.0

    datasets = parquet_store.list_datasets()
    freshness = datasets[0]["freshness"] if datasets else "no-datasets"
    regime = "unclassified"
    if datasets:
        try:
            frame = parquet_store.read_ohlcv(datasets[0]["symbol"])
            if not frame.empty:
                regime = str(current_regime(frame["close"]).get("regime", "unclassified"))
        except Exception:  # noqa: BLE001
            regime = "unclassified"

    loop = get_loop_controller().snapshot()
    return DashboardSnapshot(
        app_name=settings.app_name,
        research_score=round(score, 3),
        ai_tasks=[
            {
                "id": "loop",
                "agent": "ceo",
                "title": f"Research loop: {loop['status']}",
                "status": loop["status"],
                "cycles": loop["cycles_completed"],
            }
        ],
        queued_experiments=queued,
        completed_experiments=completed,
        rejected_strategies=rejected,
        top_strategies=[
            {"id": str(s.id), "name": s.name, "idea": s.idea[:160]} for s in strategies[:5]
        ],
        market_regime=regime,
        data_freshness=str(freshness),
        system_health={
            "api": "ok",
            "database": "ok",
            "datasets": len(datasets),
            "redis": "configured" if settings.redis_url else "missing",
            "research_loop": loop["status"],
        },
        recent_discoveries=[
            {
                "experiment_id": str(e.id),
                "status": e.status,
                "summary": e.ai_summary[:200],
            }
            for e in experiments[:5]
        ],
        timeline=[
            {
                "ts": e.created_at.isoformat() if e.created_at else "",
                "event": f"experiment:{e.status}",
                "detail": e.ai_summary[:160] or str(e.id),
            }
            for e in experiments[:8]
        ],
    )


@router.get("/meta/nav")
def navigation() -> dict[str, Any]:
    settings = get_settings()
    features = settings.yaml_config.get("features", {})
    sections = [
        {"id": "dashboard", "label": "Dashboard", "href": "/"},
        {"id": "research", "label": "Research", "href": "/research"},
        {"id": "experiments", "label": "Experiments", "href": "/experiments"},
        {"id": "strategies", "label": "Strategies", "href": "/strategies"},
        {"id": "datasets", "label": "Datasets", "href": "/datasets"},
        {
            "id": "trends",
            "label": "Trends",
            "href": "/trends",
            "enabled": bool(features.get("google_trends_enabled", False)),
        },
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


# --- CRUD ---


@router.post("/hypotheses", response_model=HypothesisOut)
def create_hypothesis(body: HypothesisCreate, db: Session = Depends(get_db)) -> Hypothesis:
    row = Hypothesis(
        title=body.title,
        thesis=body.thesis,
        rationale=body.rationale,
        family=body.family,
        tags=body.tags,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    write_audit("hypothesis_created", details={"id": str(row.id)})
    return row


@router.get("/hypotheses", response_model=list[HypothesisOut])
def list_hypotheses(db: Session = Depends(get_db)) -> list[Hypothesis]:
    return list(db.scalars(select(Hypothesis).order_by(Hypothesis.created_at.desc()).limit(200)))


@router.post("/strategies", response_model=StrategyOut)
def create_strategy(body: StrategyCreate, db: Session = Depends(get_db)) -> Strategy:
    row = Strategy(
        name=body.name,
        idea=body.idea,
        logic_summary=body.logic_summary,
        code=body.code,
        hypothesis_id=body.hypothesis_id,
        parameters=body.parameters,
        regimes=body.regimes,
        weaknesses=body.weaknesses,
        improvements=body.improvements,
        ai_notes=body.ai_notes,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/strategies", response_model=list[StrategyOut])
def list_strategies(db: Session = Depends(get_db)) -> list[Strategy]:
    return list(db.scalars(select(Strategy).order_by(Strategy.created_at.desc()).limit(200)))


@router.get("/strategies/{strategy_id}", response_model=StrategyOut)
def get_strategy(strategy_id: UUID, db: Session = Depends(get_db)) -> Strategy:
    row = db.get(Strategy, strategy_id)
    if not row:
        raise HTTPException(404, "Strategy not found")
    return row


@router.post("/experiments", response_model=ExperimentOut)
def create_experiment(body: ExperimentCreate, db: Session = Depends(get_db)) -> Experiment:
    row = Experiment(
        strategy_id=body.strategy_id,
        status=body.status,
        inputs=body.inputs,
        outputs=body.outputs,
        metrics=body.metrics,
        reasoning=body.reasoning,
        ai_summary=body.ai_summary,
        rejection_reason=body.rejection_reason,
        tags=body.tags,
        dependencies=body.dependencies,
        reproducibility_score=body.reproducibility_score,
        confidence=body.confidence,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/experiments", response_model=list[ExperimentOut])
def list_experiments(db: Session = Depends(get_db)) -> list[Experiment]:
    return list(db.scalars(select(Experiment).order_by(Experiment.created_at.desc()).limit(200)))


@router.get("/experiments/{experiment_id}", response_model=ExperimentOut)
def get_experiment(experiment_id: UUID, db: Session = Depends(get_db)) -> Experiment:
    row = db.get(Experiment, experiment_id)
    if not row:
        raise HTTPException(404, "Experiment not found")
    return row


# --- Data plane ---


@router.get("/data/providers")
def data_providers() -> dict[str, Any]:
    return {"providers": get_registry().list_data_providers()}


@router.post("/data/ingest")
def ingest(body: IngestRequest) -> dict[str, Any]:
    provider = get_registry().get_data_provider(body.provider)
    rows = provider.get_ohlcv(body.symbol, body.start, body.end, timeframe=body.timeframe)
    path = parquet_store.write_ohlcv(body.symbol, rows, timeframe=body.timeframe)
    write_audit(
        "data_ingest",
        details={"symbol": body.symbol, "rows": len(rows), "provider": provider.name},
    )
    return {"symbol": body.symbol.upper(), "rows": len(rows), "path": str(path), "provider": provider.name}


@router.get("/datasets")
def datasets() -> dict[str, Any]:
    return {"datasets": parquet_store.list_datasets()}


@router.get("/datasets/{symbol}")
def dataset_detail(symbol: str, timeframe: str = "1d") -> dict[str, Any]:
    frame = parquet_store.read_ohlcv(symbol, timeframe=timeframe)
    if frame.empty:
        raise HTTPException(404, "Dataset not found — ingest first")
    return {
        "symbol": symbol.upper(),
        "timeframe": timeframe,
        "rows": len(frame),
        "head": frame.head(5).to_dict(orient="records"),
        "tail": frame.tail(5).to_dict(orient="records"),
        "schema": list(frame.columns),
    }


# --- Quant ---


@router.post("/backtests/run")
def run_backtest(body: BacktestRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    settings = get_settings()
    end = body.end or date.today()
    start = body.start or (end - timedelta(days=365))
    provider = get_registry().get_data_provider(body.provider)
    rows = provider.get_ohlcv(body.symbol, start, end)
    parquet_store.write_ohlcv(body.symbol, rows)
    bars = pd.DataFrame(rows)
    if body.family == "mean_reversion":
        signals = mean_reversion_signals(bars["close"])
        signal_fn = mean_reversion_signals
        code = "mean_reversion_signals(close)"
    else:
        signals = sma_crossover_signals(bars["close"])
        signal_fn = sma_crossover_signals
        code = "sma_crossover_signals(close)"

    bt = settings.yaml_config.get("backtest", {})
    config = BacktestConfig(
        initial_cash=float(bt.get("default_initial_cash", 1_000_000)),
        fee_bps=float(bt.get("fee_bps", 3)),
        slippage_bps=float(bt.get("slippage_bps", 2)),
    )
    val = settings.yaml_config.get("validation", {})
    result = validate_strategy(
        bars,
        signals,
        signal_fn=signal_fn,
        config=config,
        require_walk_forward=bool(val.get("require_walk_forward", True)),
        require_oos=bool(val.get("require_out_of_sample", True)),
    )
    payload: dict[str, Any] = {
        "symbol": body.symbol.upper(),
        "family": body.family,
        "code": code,
        "accepted": result["accepted"],
        "rejection_reasons": result["rejection_reasons"],
        "metrics": result["metrics"],
        "checks": result["checks"],
        "equity_curve": result["equity_curve"][-100:],
        "trades": result["trades"][:50],
    }
    if body.persist:
        strat = Strategy(
            name=f"{body.family}:{body.symbol}",
            idea=f"Hypothesis-driven {body.family} on {body.symbol}",
            logic_summary=code,
            code=code,
            parameters={"family": body.family},
            weaknesses="; ".join(result["rejection_reasons"]),
        )
        db.add(strat)
        db.flush()
        exp = Experiment(
            strategy_id=strat.id,
            status="accepted" if result["accepted"] else "rejected",
            inputs={"symbol": body.symbol, "family": body.family, "start": str(start), "end": str(end)},
            outputs={"n_trades": len(result["trades"])},
            metrics=result["metrics"],
            reasoning=str(result["checks"])[:8000],
            ai_summary=f"{'Accepted' if result['accepted'] else 'Rejected'} {body.family} on {body.symbol}",
            rejection_reason="; ".join(result["rejection_reasons"]),
            tags=[body.family, body.symbol.lower()],
            reproducibility_score=0.85,
            confidence=0.5,
        )
        db.add(exp)
        db.commit()
        payload["strategy_id"] = str(strat.id)
        payload["experiment_id"] = str(exp.id)
    return payload


@router.get("/regimes/{symbol}")
def regimes(symbol: str) -> dict[str, Any]:
    frame = parquet_store.read_ohlcv(symbol)
    if frame.empty:
        end = date.today()
        start = end - timedelta(days=365)
        rows = get_registry().get_data_provider().get_ohlcv(symbol, start, end)
        parquet_store.write_ohlcv(symbol, rows)
        frame = pd.DataFrame(rows)
    classified = classify_regimes(frame["close"])
    return {
        "symbol": symbol.upper(),
        "current": current_regime(frame["close"]),
        "series": classified.tail(60).to_dict(orient="records"),
    }


@router.post("/portfolio/analyze")
def portfolio_analyze(body: PortfolioRequest) -> dict[str, Any]:
    curves: dict[str, list[float]] = {}
    end = date.today()
    start = end - timedelta(days=365)
    provider = get_registry().get_data_provider()
    for symbol in body.symbols:
        rows = provider.get_ohlcv(symbol, start, end)
        parquet_store.write_ohlcv(symbol, rows)
        bars = pd.DataFrame(rows)
        signals = sma_crossover_signals(bars["close"])
        from quant_os_api.quant.backtest import run_bar_backtest

        result = run_bar_backtest(bars, signals)
        curves[symbol] = [p["equity"] for p in result.equity_curve]
    return portfolio_report(curves)


# --- AI ---


@router.post("/ai/cycle")
def ai_cycle(body: ResearchCycleRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    result = run_research_cycle(
        symbol=body.symbol,
        lookback_days=body.lookback_days,
        seed=body.seed,
        provider_name=body.provider,
    )
    persisted = None
    if body.persist:
        persisted = persist_loop_result(db, result)
    return {
        "run_id": result.run_id,
        "accepted": result.accepted,
        "hypothesis": result.hypothesis,
        "strategy": result.strategy,
        "experiment": result.experiment,
        "events": [{"agent": e.agent, "message": e.message, "data": e.data} for e in result.events],
        "persisted": persisted,
    }


@router.post("/ai/chat")
def ai_chat(body: ChatRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    summary = None
    if body.experiment_ids:
        try:
            exp = db.get(Experiment, UUID(body.experiment_ids[0]))
            if exp:
                summary = exp.ai_summary
        except Exception:  # noqa: BLE001
            summary = None
    return llm_chat(
        body.messages,
        context={"experiment_ids": body.experiment_ids, "summary": summary},
    )


@router.get("/ai/loop")
def ai_loop_status() -> dict[str, Any]:
    return get_loop_controller().snapshot()


@router.post("/ai/loop/start")
def ai_loop_start(body: LoopControlRequest) -> dict[str, Any]:
    return get_loop_controller().start(
        symbols=body.symbols,
        provider=body.provider,
        interval_seconds=body.interval_seconds,
        max_cycles=body.max_cycles,
    )


@router.post("/ai/loop/pause")
def ai_loop_pause() -> dict[str, Any]:
    return get_loop_controller().pause()


@router.post("/ai/loop/resume")
def ai_loop_resume() -> dict[str, Any]:
    return get_loop_controller().resume()


@router.post("/ai/loop/stop")
def ai_loop_stop() -> dict[str, Any]:
    return get_loop_controller().stop()


# --- Search / logs / notebook / analytics ---


@router.get("/search")
def search(q: str = Query(min_length=1), db: Session = Depends(get_db)) -> dict[str, Any]:
    like = f"%{q}%"
    strategies = list(
        db.scalars(
            select(Strategy)
            .where(or_(Strategy.name.ilike(like), Strategy.idea.ilike(like), Strategy.code.ilike(like)))
            .limit(20)
        )
    )
    experiments = list(
        db.scalars(
            select(Experiment)
            .where(
                or_(
                    Experiment.ai_summary.ilike(like),
                    Experiment.rejection_reason.ilike(like),
                    Experiment.reasoning.ilike(like),
                )
            )
            .limit(20)
        )
    )
    hypotheses = list(
        db.scalars(
            select(Hypothesis)
            .where(or_(Hypothesis.title.ilike(like), Hypothesis.thesis.ilike(like)))
            .limit(20)
        )
    )
    return {
        "query": q,
        "strategies": [{"id": str(s.id), "name": s.name} for s in strategies],
        "experiments": [
            {"id": str(e.id), "status": e.status, "summary": e.ai_summary[:160]} for e in experiments
        ],
        "hypotheses": [{"id": str(h.id), "title": h.title} for h in hypotheses],
    }


@router.get("/logs/audit")
def audit_logs(limit: int = 100) -> dict[str, Any]:
    return {"events": read_audit(limit=limit)}


@router.get("/notebook/examples")
def notebook_examples() -> dict[str, Any]:
    return {
        "notebooks": [
            {
                "id": str(uuid4()),
                "title": "SMA momentum research template",
                "markdown": "# Momentum research\nHypothesis first, then code, then validate.",
                "code": (
                    "provider = FixtureDataProvider()\n"
                    "rows = provider.get_ohlcv('RELIANCE', date(2024,1,1), date(2024,6,1))\n"
                    "bars = pd.DataFrame(rows)\n"
                    "signals = backtest.sma_crossover_signals(bars['close'])\n"
                    "result = backtest.run_bar_backtest(bars, signals).metrics\n"
                    "print(result)\n"
                ),
            }
        ]
    }


@router.post("/notebook/execute")
def notebook_execute(body: NotebookExecuteRequest) -> dict[str, Any]:
    return execute_notebook_code(body.code)


@router.post("/analytics/sync")
def analytics_sync() -> dict[str, Any]:
    return sync_parquet_to_duckdb()


@router.post("/analytics/query")
def analytics_query(body: DuckDBQueryRequest) -> dict[str, Any]:
    try:
        return query_duckdb(body.sql, max_rows=body.max_rows)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(400, str(exc)) from exc


@router.post("/admin/seed")
def admin_seed() -> dict[str, Any]:
    result = seed_sample_data()
    write_audit("sample_data_seeded", details={"count": len(result["seeded"])})
    return result


@router.post("/security/encrypt")
def security_encrypt(body: EncryptRequest) -> dict[str, Any]:
    return encrypt_secret(body.value)


@router.post("/security/decrypt")
def security_decrypt(body: EncryptRequest) -> dict[str, Any]:
    return decrypt_secret(body.value)


# --- Google Trends Intelligence (relative 0–100 index; not absolute volume) ---


@router.get("/trends/entities")
def trends_entities() -> dict[str, Any]:
    from quant_os_api.trends.universe import entity_config, iter_queries, list_entities

    entities = []
    for eid in list_entities():
        cfg = entity_config(eid)
        entities.append(
            {
                "id": eid,
                "label": cfg.get("label"),
                "ticker": cfg.get("ticker"),
                "query_count": len(iter_queries(eid)),
            }
        )
    return {"entities": entities, "is_absolute_volume": False}


@router.get("/trends/{entity_id}/universe")
def trends_universe(entity_id: str) -> dict[str, Any]:
    from quant_os_api.trends.universe import anchor_terms, comparison_groups, entity_config, iter_queries

    try:
        cfg = entity_config(entity_id)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    return {
        "entity_id": entity_id,
        "config": {
            "label": cfg.get("label"),
            "ticker": cfg.get("ticker"),
            "core_states": cfg.get("core_states"),
            "earnings_calendar": cfg.get("earnings_calendar"),
        },
        "queries": iter_queries(entity_id),
        "anchors": anchor_terms(entity_id),
        "comparison_groups": comparison_groups(entity_id),
        "is_absolute_volume": False,
        "caveats": __import__("quant_os_api.trends", fromlist=["CAVEATS"]).CAVEATS,
    }


@router.post("/trends/collect")
def trends_collect(body: TrendsCollectRequest) -> dict[str, Any]:
    from quant_os_api.trends.collector import collect_entity

    features = get_settings().yaml_config.get("features", {})
    if not bool(features.get("google_trends_enabled", False)):
        raise HTTPException(400, "google_trends_enabled is false in config")
    try:
        result = collect_entity(body.entity_id, provider=body.provider, windows=body.windows)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    write_audit("trends_collected", details={"entity_id": body.entity_id, "run_id": result.get("run_id")})
    return result


@router.get("/trends/{entity_id}/inventory")
def trends_inventory(entity_id: str) -> dict[str, Any]:
    from quant_os_api.trends import store as trends_store

    return trends_store.inventory(entity_id)


@router.get("/trends/{entity_id}/runs")
def trends_runs(entity_id: str) -> dict[str, Any]:
    from quant_os_api.trends import store as trends_store

    return {"entity_id": entity_id, "runs": trends_store.list_runs(entity_id)}


@router.post("/trends/score")
def trends_score(body: TrendsScoreRequest) -> dict[str, Any]:
    from quant_os_api.trends.score import score_entity

    try:
        return score_entity(body.entity_id, as_of=body.as_of, window=body.window)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get("/trends/{entity_id}/dashboard")
def trends_dashboard(entity_id: str, window: str = Query("90d")) -> dict[str, Any]:
    from quant_os_api.trends.alerts import build_alerts
    from quant_os_api.trends.backtest import pre_earnings_panel
    from quant_os_api.trends.cross_signals import load_cross_signals
    from quant_os_api.trends.score import score_entity
    from quant_os_api.trends import store as trends_store

    from quant_os_api.trends import CAVEATS

    inv = trends_store.inventory(entity_id)
    if inv["interest_rows"] == 0:
        return {
            "ok": False,
            "entity_id": entity_id,
            "error": "No Trends data — run make trends-demo or POST /api/v1/trends/collect first",
            "inventory": inv,
            "is_absolute_volume": False,
            "caveats": CAVEATS,
            "empty_state": True,
            "next_steps": [
                "make trends-demo  # fixture offline seed for dmart + trent",
                "Open /trends and click Refresh",
                "Optional: make trends-train for proxy model ranking",
            ],
        }
    try:
        scored = score_entity(entity_id, window=window)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    alerts = build_alerts(entity_id, window=window)
    panel = pre_earnings_panel(entity_id)
    cross = scored.get("cross_signal") or load_cross_signals(entity_id, window=window)
    return {
        "ok": True,
        "entity_id": entity_id,
        "label": scored.get("label"),
        "ticker": scored.get("ticker"),
        "inventory": inv,
        "score": scored,
        "alerts": alerts.get("alerts", []),
        "pre_earnings": panel,
        "cross_signal": cross,
        "is_absolute_volume": False,
        "caveats": scored.get("caveats", []),
    }


@router.get("/trends/{entity_id}/alerts")
def trends_alerts(entity_id: str, window: str = Query("90d")) -> dict[str, Any]:
    from quant_os_api.trends.alerts import build_alerts

    return build_alerts(entity_id, window=window)


@router.get("/trends/{entity_id}/pre-earnings")
def trends_pre_earnings(entity_id: str, next_earnings: str | None = None) -> dict[str, Any]:
    from quant_os_api.trends.backtest import pre_earnings_panel

    return pre_earnings_panel(entity_id, next_earnings=next_earnings)


@router.post("/trends/{entity_id}/backtest")
def trends_backtest(entity_id: str) -> dict[str, Any]:
    from quant_os_api.trends.backtest import run_pre_earnings_backtest

    result = run_pre_earnings_backtest(entity_id)
    write_audit("trends_backtest", details={"entity_id": entity_id, "ok": result.get("ok")})
    return result


@router.post("/trends/collect-all")
def trends_collect_all(provider: str | None = None) -> dict[str, Any]:
    from quant_os_api.trends.collector import collect_entity
    from quant_os_api.trends.score import score_entity
    from quant_os_api.trends.universe import list_entities

    features = get_settings().yaml_config.get("features", {})
    if not bool(features.get("google_trends_enabled", False)):
        raise HTTPException(400, "google_trends_enabled is false in config")
    results = []
    for eid in list_entities():
        try:
            collected = collect_entity(eid, provider=provider)
            scored = score_entity(eid)
            results.append(
                {
                    "entity_id": eid,
                    "ok": True,
                    "run_id": collected.get("run_id"),
                    "interest_rows": collected.get("interest_rows"),
                    "search_demand_score": scored.get("search_demand_score"),
                    "quality_badge": scored.get("quality_badge"),
                }
            )
        except Exception as exc:  # noqa: BLE001
            results.append({"entity_id": eid, "ok": False, "error": str(exc)})
    write_audit("trends_collect_all", details={"n": len(results)})
    return {"ok": True, "n": len(results), "results": results, "is_absolute_volume": False}


@router.post("/trends/models/train")
def trends_models_train(body: TrendsTrainRequest) -> dict[str, Any]:
    from quant_os_api.trends.modeling import train_models

    result = train_models(entity_ids=body.entity_ids, entity_id=body.entity_id)
    write_audit("trends_models_train", details={"ok": result.get("ok"), "n_rows": (result.get("meta") or {}).get("n_rows")})
    return result


@router.post("/trends/models/predict")
def trends_models_predict(body: TrendsPredictRequest) -> dict[str, Any]:
    from quant_os_api.trends.modeling import predict_entity

    try:
        return predict_entity(body.entity_id, as_of=body.as_of, window=body.window)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get("/trends/{entity_id}/nowcast")
def trends_nowcast(entity_id: str, window: str = Query("90d")) -> dict[str, Any]:
    from quant_os_api.trends.modeling import nowcast_entity

    try:
        return nowcast_entity(entity_id, window=window)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get("/trends/{entity_id}/predict")
def trends_predict_get(entity_id: str, window: str = Query("90d")) -> dict[str, Any]:
    from quant_os_api.trends.modeling import predict_entity

    try:
        return predict_entity(entity_id, window=window)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.post("/trends/rank")
def trends_rank(body: TrendsRankRequest) -> dict[str, Any]:
    from quant_os_api.trends.modeling import rank_entities

    return rank_entities(body.entity_ids, window=body.window)


@router.get("/trends/comparison")
def trends_comparison(window: str = Query("90d")) -> dict[str, Any]:
    from quant_os_api.trends.modeling import rank_entities

    return rank_entities(window=window)


@router.get("/trends/{entity_id}/export")
def trends_export(entity_id: str, window: str = Query("90d")) -> dict[str, Any]:
    """JSON export of score, chart series, features — relative indices only."""
    from quant_os_api.trends.alerts import build_alerts
    from quant_os_api.trends.score import score_entity

    try:
        scored = score_entity(entity_id, window=window)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    if not scored.get("ok"):
        raise HTTPException(400, scored.get("error") or "export unavailable")
    alerts = build_alerts(entity_id, window=window)
    return {
        "ok": True,
        "entity_id": entity_id,
        "label": scored.get("label"),
        "ticker": scored.get("ticker"),
        "as_of": scored.get("as_of"),
        "window": window,
        "search_demand_score": scored.get("search_demand_score"),
        "quality_badge": scored.get("quality_badge"),
        "confidence_interval": scored.get("confidence_interval"),
        "components": scored.get("components"),
        "regime": scored.get("regime"),
        "features": scored.get("features"),
        "chart": scored.get("chart"),
        "heatmap": scored.get("heatmap"),
        "rising_queries": scored.get("rising_queries"),
        "cross_signal": scored.get("cross_signal"),
        "alerts": alerts.get("alerts", []),
        "is_absolute_volume": False,
        "caveats": scored.get("caveats", []),
        "export_format": "json",
    }


@router.get("/trends/{entity_id}/cross-signals")
def trends_cross_signals(entity_id: str, window: str = Query("90d")) -> dict[str, Any]:
    from quant_os_api.trends.cross_signals import load_cross_signals

    try:
        return load_cross_signals(entity_id, window=window)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
