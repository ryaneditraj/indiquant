"""Point-in-time pre-earnings Trends backtest — no post-quarter leakage."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import numpy as np

from quant_os_api.trends.score import score_entity
from quant_os_api.trends.universe import entity_config

HORIZONS = (30, 21, 14, 7, 3)


def _parse(d: str) -> date:
    return date.fromisoformat(d[:10])


def run_pre_earnings_backtest(entity_id: str = "dmart") -> dict[str, Any]:
    """
    For each configured earnings date, score using only data available
    N days before earnings (as_of cutoff). Does not use post-quarter search.
    """
    cfg = entity_config(entity_id)
    earnings = [_parse(x) for x in cfg.get("earnings_calendar") or []]
    if not earnings:
        return {"ok": False, "error": "No earnings_calendar configured"}

    # Prefer long windows so historical as_of dates still have series history.
    window = "5y"
    rows: list[dict[str, Any]] = []
    for ed in earnings:
        if ed > date.today() + timedelta(days=1):
            continue
        for h in HORIZONS:
            as_of = (ed - timedelta(days=h)).isoformat()
            scored = score_entity(entity_id, as_of=as_of, window=window)
            if not scored.get("ok"):
                # Fall back to 12m then 90d
                for w in ("12m", "90d"):
                    scored = score_entity(entity_id, as_of=as_of, window=w)
                    if scored.get("ok"):
                        window = w
                        break
            if not scored.get("ok"):
                continue
            rows.append(
                {
                    "earnings_date": ed.isoformat(),
                    "horizon_days_before": h,
                    "collection_as_of": as_of,
                    "economic_interpretation_date": ed.isoformat(),
                    "window": window,
                    "search_demand_score": scored["search_demand_score"],
                    "regime": scored["regime"],
                    "quality_badge": scored["quality_badge"],
                    "confidence_interval": scored["confidence_interval"],
                    "components": scored["components"],
                    "pre_earn_14d": scored["features"].get("pre_earn_14d"),
                    "leakage_guard": "as_of < earnings_date; series truncated to date<=as_of",
                }
            )

    if not rows:
        return {
            "ok": False,
            "error": "No scorable earnings windows — collect Trends history first",
            "entity_id": entity_id,
        }

    # Synthetic evaluation targets (Phase 1): regime stability proxies.
    # Real revenue/SSS labels plug in when fundamentals store exists.
    regimes = [r["regime"] for r in rows if r["horizon_days_before"] == 14]
    bullish = sum(1 for r in regimes if r == "bullish")
    bearish = sum(1 for r in regimes if r == "bearish")
    neutral = sum(1 for r in regimes if r == "neutral")

    scores_14 = [r["search_demand_score"] for r in rows if r["horizon_days_before"] == 14]
    # Placeholder MAE vs mean score (until labeled revenue growth available)
    if scores_14:
        mu = float(np.mean(scores_14))
        mae_proxy = float(np.mean([abs(s - mu) for s in scores_14]))
    else:
        mae_proxy = None

    # Incremental lift proxies using fixture cross-signals when available
    lift_sat = None
    lift_app = None
    try:
        from quant_os_api.trends.cross_signals import load_cross_signals

        xs = load_cross_signals(entity_id, window="90d")
        m = xs.get("metrics") or {}
        corr_s = m.get("corr_satellite")
        corr_a = m.get("corr_app_rank")
        # Lift proxy: fraction of absolute confirmation strength
        if corr_s is not None:
            lift_sat = round(float(abs(corr_s)) * 0.12, 4)
        if corr_a is not None:
            lift_app = round(float(abs(corr_a)) * 0.08 + float(abs(m.get("corr_pricing_promo") or 0)) * 0.04, 4)
    except Exception:  # noqa: BLE001
        pass

    return {
        "ok": True,
        "entity_id": entity_id,
        "is_absolute_volume": False,
        "horizons_days_before": list(HORIZONS),
        "n_observations": len(rows),
        "observations": rows,
        "metrics": {
            "score_dispersion_mae_proxy": mae_proxy,
            "regime_counts_14d": {"bullish": bullish, "neutral": neutral, "bearish": bearish},
            "hit_rate_note": (
                "Labeled beat/miss and revenue growth targets not yet wired — "
                "reporting regime distribution + score stability; model layer uses proxy labels."
            ),
            "incremental_lift_satellite": lift_sat,
            "incremental_lift_app_pricing": lift_app,
        },
        "guards": [
            "Point-in-time as_of cutoff strictly before earnings_date",
            "Query collection timestamp separate from economic interpretation date",
            "No post-quarter search features in pre-earnings score",
        ],
    }


def pre_earnings_panel(entity_id: str = "dmart", *, next_earnings: str | None = None) -> dict[str, Any]:
    cfg = entity_config(entity_id)
    calendar = sorted(_parse(x) for x in cfg.get("earnings_calendar") or [])
    today = date.today()
    if next_earnings:
        nxt = _parse(next_earnings)
    else:
        future = [d for d in calendar if d >= today]
        nxt = future[0] if future else (calendar[-1] if calendar else today)

    scored = score_entity(entity_id, window="90d")
    history = []
    for ed in calendar[-6:]:
        as_of = (ed - timedelta(days=14)).isoformat()
        s = score_entity(entity_id, as_of=as_of, window="90d")
        if s.get("ok"):
            history.append(
                {
                    "earnings_date": ed.isoformat(),
                    "score_14d_before": s["search_demand_score"],
                    "regime": s["regime"],
                    "quality_badge": s["quality_badge"],
                }
            )

    surprise = None
    if scored.get("ok") and history:
        baseline = float(np.mean([h["score_14d_before"] for h in history]))
        surprise = round(float(scored["search_demand_score"]) - baseline, 2)

    return {
        "entity_id": entity_id,
        "next_earnings_date": nxt.isoformat(),
        "days_to_earnings": (nxt - today).days,
        "current": scored if scored.get("ok") else None,
        "search_surprise_vs_trailing": surprise,
        "historical_pre_earnings": history,
        "classification": scored.get("regime") if scored.get("ok") else "neutral",
        "confidence_interval": scored.get("confidence_interval") if scored.get("ok") else None,
        "is_absolute_volume": False,
        "caveats": scored.get("caveats") if scored.get("ok") else [],
    }
