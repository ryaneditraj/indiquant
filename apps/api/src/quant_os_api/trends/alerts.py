"""Rule-based Trends alerts with NL explanations from observed features only."""

from __future__ import annotations

from typing import Any

from quant_os_api.trends.score import score_entity
from quant_os_api.trends.universe import trends_config


def _safe(v: Any, default: float = 0.0) -> float:
    try:
        if v is None:
            return default
        return float(v)
    except (TypeError, ValueError):
        return default


def build_alerts(entity_id: str = "dmart", *, as_of: str | None = None, window: str = "90d") -> dict[str, Any]:
    scored = score_entity(entity_id, as_of=as_of, window=window)
    if not scored.get("ok"):
        return {"entity_id": entity_id, "alerts": [], "error": scored.get("error")}

    f = scored["features"]
    thr = trends_config().get("alert_thresholds") or {}
    badge = scored.get("quality_badge", "medium")
    alerts: list[dict[str, Any]] = []

    def add(
        kind: str,
        *,
        direction: str,
        magnitude: float,
        explanation: str,
        query_group: str,
    ) -> None:
        alerts.append(
            {
                "kind": kind,
                "direction": direction,
                "magnitude": round(magnitude, 4),
                "confidence": badge,
                "explanation": explanation,
                "query_group": query_group,
                "as_of": scored["as_of"],
                "is_absolute_volume": False,
            }
        )

    z = _safe(f.get("zscore_1y"))
    accel = _safe(f.get("trend_acceleration"))
    if z >= float(thr.get("brand_accel", 1.5)) or accel > 0.3:
        add(
            "brand_search_acceleration",
            direction="up",
            magnitude=max(z, accel),
            explanation=(
                f"Brand interest z-score={z:.2f} with acceleration={accel:.2f} "
                "versus rolling history (relative index)."
            ),
            query_group="brand_vs_anchor",
        )

    tx_ratio = _safe(f.get("transactional_to_brand_ratio"), 0.5)
    if tx_ratio >= float(thr.get("transactional_surge", 2.0)) / 2.0 + 0.4:
        add(
            "transactional_query_surge",
            direction="up",
            magnitude=tx_ratio,
            explanation=(
                f"Transactional-to-brand ratio at {tx_ratio:.2f}, "
                "indicating elevated purchase-intent query mix."
            ),
            query_group="tx_vs_brand",
        )

    share = _safe(f.get("relative_search_share"), 0.3)
    if share >= 0.3 + float(thr.get("share_breakout", 0.08)):
        add(
            "competitor_relative_share_breakout",
            direction="up",
            magnitude=share,
            explanation=(
                f"Brand share inside competitor comparison group rose to {share:.1%} "
                "(within-request relative index)."
            ),
            query_group="competitor_basket",
        )

    risk_z = _safe(f.get("risk_last")) / max(_safe(f.get("brand_last"), 1.0), 1.0)
    if _safe(f.get("risk_query_ratio")) >= 0.35 or risk_z * 10 >= float(thr.get("risk_spike", 2.5)):
        add(
            "risk_query_spike",
            direction="up",
            magnitude=_safe(f.get("risk_query_ratio")),
            explanation=f"Risk/friction query ratio at {_safe(f.get('risk_query_ratio')):.2f} versus brand attention.",
            query_group="risk_vs_brand",
        )

    if _safe(f.get("core_vs_noncore_spread")) > 15:
        add(
            "region_specific_anomaly",
            direction="up",
            magnitude=_safe(f.get("core_vs_noncore_spread")),
            explanation=(
                "Core-state interest exceeds non-core by "
                f"{_safe(f.get('core_vs_noncore_spread')):.1f} index points."
            ),
            query_group="brand_vs_anchor",
        )

    # Cross-signal divergence alerts (fixture adapters produce real metrics offline)
    if f.get("divergence_satellite") is not None and abs(_safe(f.get("divergence_satellite"))) >= 0.15:
        add(
            "search_satellite_divergence",
            direction="warn",
            magnitude=_safe(f.get("divergence_satellite")),
            explanation=(
                f"Search vs satellite parking divergence={_safe(f.get('divergence_satellite')):.2f} "
                f"(corr={_safe(f.get('corr_satellite')):.2f}); confirmatory channel disagreement."
            ),
            query_group="cross_signal",
        )

    if f.get("divergence_app_rank") is not None and abs(_safe(f.get("divergence_app_rank"))) >= 0.18:
        add(
            "search_app_divergence",
            direction="warn",
            magnitude=_safe(f.get("divergence_app_rank")),
            explanation=(
                f"Search vs app-rank divergence={_safe(f.get('divergence_app_rank')):.2f} "
                f"(corr={_safe(f.get('corr_app_rank')):.2f})."
            ),
            query_group="cross_signal",
        )

    mom = _safe(f.get("pre_earn_14d"), _safe(f.get("growth_2w")))
    if abs(mom) >= 0.1 and badge != "unreliable":
        add(
            "pre_earnings_momentum_breakout",
            direction="up" if mom > 0 else "down",
            magnitude=mom,
            explanation=f"Pre-earnings search momentum at {mom:.1%} versus trailing baseline (relative index).",
            query_group="brand_vs_anchor",
        )

    return {
        "entity_id": entity_id,
        "as_of": scored["as_of"],
        "quality_badge": badge,
        "alerts": alerts,
        "caveats": scored.get("caveats"),
    }
