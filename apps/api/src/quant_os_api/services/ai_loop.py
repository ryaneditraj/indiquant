"""AI research loop — hypothesis-first; works offline without API keys."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any
from uuid import uuid4

import pandas as pd

from quant_os_api.config import get_settings
from quant_os_api.plugins.registry import get_registry
from quant_os_api.quant.backtest import (
    BacktestConfig,
    mean_reversion_signals,
    sma_crossover_signals,
)
from quant_os_api.quant.regimes import current_regime
from quant_os_api.quant.validation import reproducibility_score, validate_strategy
from quant_os_api.services import parquet_store

STRATEGY_FAMILIES = [
    {
        "family": "momentum",
        "title": "Intermediate momentum via SMA crossover",
        "thesis": "Persistently trending NSE names continue over multi-week horizons.",
        "rationale": "Cross-sectional and time-series momentum are documented; we test a simple SMA rule with costs.",
        "builder": "sma",
    },
    {
        "family": "mean_reversion",
        "title": "Short-term mean reversion on z-score dips",
        "thesis": "Liquidity-driven overreactions reverse within days in liquid large-caps.",
        "rationale": "Mean reversion after large z-score deviations; must survive costs and regime filters.",
        "builder": "mean_reversion",
    },
]


@dataclass
class AgentEvent:
    agent: str
    message: str
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class LoopResult:
    run_id: str
    events: list[AgentEvent]
    hypothesis: dict[str, Any]
    strategy: dict[str, Any]
    experiment: dict[str, Any]
    accepted: bool


def _pick_family(symbol: str, seed: int) -> dict[str, Any]:
    digest = int(hashlib.sha256(f"{symbol}:{seed}".encode()).hexdigest(), 16)
    return STRATEGY_FAMILIES[digest % len(STRATEGY_FAMILIES)]


def run_research_cycle(
    *,
    symbol: str = "RELIANCE",
    lookback_days: int = 365,
    seed: int = 42,
    provider_name: str | None = None,
) -> LoopResult:
    """CEO-orchestrated single cycle: Research → Quant → Backtest → Statistician → Critic → Risk."""
    settings = get_settings()
    bt_cfg_raw = settings.yaml_config.get("backtest", {})
    val_cfg = settings.yaml_config.get("validation", {})
    config = BacktestConfig(
        initial_cash=float(bt_cfg_raw.get("default_initial_cash", 1_000_000)),
        fee_bps=float(bt_cfg_raw.get("fee_bps", 3.0)),
        slippage_bps=float(bt_cfg_raw.get("slippage_bps", 2.0)),
    )
    events: list[AgentEvent] = []
    run_id = str(uuid4())

    events.append(AgentEvent("ceo", "Starting research cycle", {"run_id": run_id, "symbol": symbol}))

    # Data agent
    end = date.today()
    start = end - timedelta(days=lookback_days)
    registry = get_registry()
    provider = registry.get_data_provider(provider_name)
    events.append(
        AgentEvent("data", f"Fetching OHLCV via {provider.name}", {"start": str(start), "end": str(end)})
    )
    rows = provider.get_ohlcv(symbol, start, end, timeframe="1d")
    parquet_store.write_ohlcv(symbol, rows, timeframe="1d")
    bars = pd.DataFrame(rows)
    if bars.empty:
        raise RuntimeError("No bars returned from data provider")

    regime = current_regime(bars["close"])
    events.append(AgentEvent("data", "Market regime snapshot", regime))

    # Research agent — hypothesis first (never random indicator soup)
    family = _pick_family(symbol, seed)
    hypothesis = {
        "id": str(uuid4()),
        "title": family["title"],
        "thesis": family["thesis"],
        "rationale": family["rationale"],
        "family": family["family"],
        "tags": [family["family"], "india", "nse", symbol.lower()],
    }
    events.append(AgentEvent("research", "Hypothesis generated", hypothesis))

    # Quant agent
    if family["builder"] == "sma":
        signals = sma_crossover_signals(bars["close"], fast=10, slow=30)
        code = "sma_crossover_signals(close, fast=10, slow=30)"
        params = {"fast": 10, "slow": 30}
        signal_fn = lambda c: sma_crossover_signals(c, fast=10, slow=30)  # noqa: E731
    else:
        signals = mean_reversion_signals(bars["close"], lookback=20, z=1.0)
        code = "mean_reversion_signals(close, lookback=20, z=1.0)"
        params = {"lookback": 20, "z": 1.0}
        signal_fn = lambda c: mean_reversion_signals(c, lookback=20, z=1.0)  # noqa: E731

    strategy = {
        "id": str(uuid4()),
        "name": f"{family['family']}:{symbol}",
        "idea": hypothesis["thesis"],
        "logic_summary": family["rationale"],
        "code": code,
        "parameters": params,
        "regimes": [regime.get("regime")],
    }
    events.append(AgentEvent("quant", "Strategy materialized from hypothesis", strategy))

    # Backtest + Statistician + Critic + Risk (validation suite)
    events.append(AgentEvent("backtest", "Running bar engine with fees/slippage"))
    validation = validate_strategy(
        bars,
        signals,
        signal_fn=signal_fn,
        config=config,
        require_walk_forward=bool(val_cfg.get("require_walk_forward", True)),
        require_oos=bool(val_cfg.get("require_out_of_sample", True)),
    )
    events.append(
        AgentEvent(
            "statistician",
            "Validation complete",
            {"accepted": validation["accepted"], "reasons": validation["rejection_reasons"]},
        )
    )
    if validation["rejected"]:
        events.append(
            AgentEvent(
                "critic",
                "Rejecting strategy — failed scientific gates",
                {"reasons": validation["rejection_reasons"]},
            )
        )
    else:
        events.append(AgentEvent("critic", "No fatal flaws in validation gates"))

    events.append(
        AgentEvent(
            "risk",
            "Risk snapshot",
            {
                "max_drawdown": validation["metrics"].get("max_drawdown"),
                "volatility": validation["metrics"].get("volatility"),
                "monte_carlo": validation["checks"].get("monte_carlo"),
            },
        )
    )

    inputs = {
        "symbol": symbol,
        "start": str(start),
        "end": str(end),
        "seed": seed,
        "provider": provider.name,
        "strategy_family": family["family"],
        "parameters": params,
        "code_version": "0.1.0",
    }
    repro = reproducibility_score(inputs, validation["metrics"])
    min_repro = float(val_cfg.get("min_reproducibility_score", 0.7))
    accepted = validation["accepted"] and repro >= min_repro
    if not accepted and repro < min_repro:
        validation["rejection_reasons"].append("reproducibility_score_below_threshold")

    experiment = {
        "id": str(uuid4()),
        "status": "accepted" if accepted else "rejected",
        "inputs": inputs,
        "outputs": {
            "equity_curve": validation["equity_curve"][-50:],  # trim for storage
            "n_trades": len(validation["trades"]),
            "regime": regime,
        },
        "metrics": validation["metrics"],
        "reasoning": json.dumps(validation["checks"], default=str)[:8000],
        "ai_summary": (
            f"{'Accepted' if accepted else 'Rejected'} {family['family']} on {symbol}. "
            f"Sharpe={validation['metrics'].get('sharpe', 0):.3f}, "
            f"MaxDD={validation['metrics'].get('max_drawdown', 0):.3f}."
        ),
        "rejection_reason": "; ".join(validation["rejection_reasons"]),
        "tags": hypothesis["tags"],
        "reproducibility_score": repro,
        "confidence": float(regime.get("confidence", 0.0)),
    }
    events.append(AgentEvent("documentation", "Experiment documented", {"experiment_id": experiment["id"]}))
    events.append(AgentEvent("ceo", "Cycle complete", {"accepted": accepted}))

    return LoopResult(
        run_id=run_id,
        events=events,
        hypothesis=hypothesis,
        strategy=strategy,
        experiment=experiment,
        accepted=accepted,
    )


def llm_chat(messages: list[dict[str, str]], *, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Project-aware chat. Uses OpenAI-compatible API when keyed; otherwise deterministic offline reply."""
    settings = get_settings()
    context = context or {}
    citations = context.get("experiment_ids") or []
    user_text = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")

    if settings.ai_openai_compatible_api_key:
        try:
            import httpx

            payload = {
                "model": settings.ai_default_model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are the research OS assistant. Never invent metrics. "
                            "Cite experiment IDs when discussing results. "
                            f"Known experiment IDs: {citations}"
                        ),
                    },
                    *messages,
                ],
                "temperature": float(settings.yaml_config.get("ai", {}).get("temperature", 0.2)),
            }
            headers = {
                "Authorization": f"Bearer {settings.ai_openai_compatible_api_key}",
                "Content-Type": "application/json",
            }
            url = settings.ai_openai_compatible_base_url.rstrip("/") + "/chat/completions"
            with httpx.Client(timeout=60.0) as client:
                resp = client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return {"role": "assistant", "content": content, "citations": citations, "mode": "llm"}
        except Exception as exc:  # noqa: BLE001
            return {
                "role": "assistant",
                "content": f"LLM call failed ({exc}). Falling back to offline mode.",
                "citations": citations,
                "mode": "error-fallback",
            }

    # Offline deterministic assistant — never hallucinate metrics
    reply = (
        "Offline AI mode (no AI_OPENAI_COMPATIBLE_API_KEY). "
        "I can only reference provided context — I will not invent metrics.\n\n"
        f"You asked: {user_text[:500]}\n"
    )
    if citations:
        reply += f"Cited experiment IDs: {', '.join(map(str, citations))}\n"
    if context.get("summary"):
        reply += f"Context summary: {context['summary']}\n"
    else:
        reply += (
            "No experiment summary in context. Run a research cycle or pass experiment_ids "
            "so answers stay evidence-based.\n"
        )
    return {"role": "assistant", "content": reply, "citations": citations, "mode": "offline"}
