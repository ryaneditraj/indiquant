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
    ExperimentCreate,
    ExperimentOut,
    HealthResponse,
    HypothesisCreate,
    HypothesisOut,
    IngestRequest,
    PortfolioRequest,
    ResearchCycleRequest,
    SettingsPublicResponse,
    StrategyCreate,
    StrategyOut,
)
from quant_os_api.services import parquet_store
from quant_os_api.services.ai_loop import llm_chat, run_research_cycle
from quant_os_api.services.audit import read_audit, write_audit
from quant_os_api.services.persistence import persist_loop_result
from quant_os_api.services.portfolio import portfolio_report

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

    return DashboardSnapshot(
        app_name=settings.app_name,
        research_score=round(score, 3),
        ai_tasks=[
            {
                "id": "loop",
                "agent": "ceo",
                "title": "Research loop ready — POST /api/v1/ai/cycle",
                "status": "idle",
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


# --- Search / logs / notebook ---


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
                "code": "from quant_os_api.quant.backtest import sma_crossover_signals\nprint('ready')",
            }
        ]
    }
