"""Search Demand Score — interpretable subcomponents + confidence."""

from __future__ import annotations

from typing import Any

from quant_os_api.trends import CAVEATS, QUALITY_BADGES
from quant_os_api.trends.features import compute_features
from quant_os_api.trends import store as trends_store
from quant_os_api.trends.universe import trends_config


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _safe(v: Any, default: float = 0.0) -> float:
    try:
        if v is None:
            return default
        return float(v)
    except (TypeError, ValueError):
        return default


def _quality_badge(features: dict[str, Any]) -> str:
    sparse = features.get("sparsity") or {}
    if sparse.get("sparse") or sparse.get("unstable"):
        return "unreliable"
    vol = _safe(features.get("volatility"), 0)
    z = abs(_safe(features.get("zscore_1y"), 0))
    if vol > 25 or z > 3.5:
        return "low"
    if vol > 12 or sparse.get("zero_share", 0) > 0.1:
        return "medium"
    return "high"


def score_entity(entity_id: str = "dmart", *, as_of: str | None = None, window: str = "90d") -> dict[str, Any]:
    feat_payload = compute_features(entity_id, as_of=as_of, window=window)
    if not feat_payload.get("ok"):
        return {
            **feat_payload,
            "score": None,
            "is_absolute_volume": False,
            "caveats": CAVEATS,
        }

    f = feat_payload["features"]
    weights = (trends_config().get("score_weights") or {}).copy()

    brand_attention = _clip01(
        0.5 + 0.25 * _safe(f.get("zscore_1y")) + 0.2 * _safe(f.get("trend_slope")) / 5.0
    )
    purchase_intent = _clip01(
        0.45
        + 0.35 * _safe(f.get("transactional_to_brand_ratio"), 0.5)
        + 0.2 * (_safe(f.get("related_query_breadth")) / 10.0)
    )
    regional = _clip01(
        0.4
        + 0.004 * _safe(f.get("state_weighted_search_score"), 50)
        + 0.01 * _safe(f.get("core_vs_noncore_spread"))
    )
    competitive = _clip01(0.3 + 0.7 * _safe(f.get("relative_search_share"), 0.3))
    # Higher risk ratio → lower component
    risk_friction = _clip01(1.0 - 1.5 * _safe(f.get("risk_query_ratio"), 0.1))
    badge = _quality_badge(f)
    quality_map = {"high": 0.95, "medium": 0.7, "low": 0.45, "unreliable": 0.2}
    signal_quality = quality_map.get(badge, 0.5)

    components = {
        "brand_attention": round(brand_attention, 4),
        "purchase_intent": round(purchase_intent, 4),
        "regional_strength": round(regional, 4),
        "competitive_share": round(competitive, 4),
        "risk_friction": round(risk_friction, 4),
        "signal_quality": round(signal_quality, 4),
    }

    # Normalize weights
    wsum = sum(float(weights.get(k, 0)) for k in components) or 1.0
    score = sum(components[k] * float(weights.get(k, 0)) / wsum for k in components)
    score_100 = round(100.0 * score, 2)

    # Regime classification for pre-earnings panel
    mom = _safe(f.get("pre_earn_14d"), _safe(f.get("growth_2w")))
    share_delta = _safe(f.get("relative_search_share"), 0.3) - 0.3
    if badge == "unreliable":
        regime = "neutral"
        regime_reason = "Sparse/unstable Trends sample — withhold directional call."
    elif mom > 0.08 and share_delta >= 0 and components["risk_friction"] > 0.55:
        regime = "bullish"
        regime_reason = "Brand/transactional momentum with stable competitive share and contained risk queries."
    elif mom < -0.08 or components["risk_friction"] < 0.4:
        regime = "bearish"
        regime_reason = "Negative search momentum and/or elevated risk/friction query pressure."
    else:
        regime = "neutral"
        regime_reason = "Search demand near baseline; no clear pre-earnings skew."

    # Crude confidence interval from sampling + sparsity
    half_width = {"high": 4.0, "medium": 8.0, "low": 14.0, "unreliable": 22.0}[badge]

    payload = {
        "entity_id": entity_id,
        "label": feat_payload.get("label"),
        "ticker": feat_payload.get("ticker"),
        "as_of": feat_payload["as_of"],
        "window": window,
        "ok": True,
        "is_absolute_volume": False,
        "search_demand_score": score_100,
        "components": components,
        "weights": {k: float(weights.get(k, 0)) / wsum for k in components},
        "quality_badge": badge,
        "quality_badges_allowed": list(QUALITY_BADGES),
        "confidence_interval": {
            "low": round(max(0.0, score_100 - half_width), 2),
            "high": round(min(100.0, score_100 + half_width), 2),
            "method": "heuristic_sampling_band",
        },
        "regime": regime,
        "regime_reason": regime_reason,
        "features": f,
        "chart": feat_payload.get("chart"),
        "heatmap": feat_payload.get("heatmap"),
        "rising_queries": feat_payload.get("rising_queries"),
        "cross_signal": feat_payload.get("cross_signal"),
        "caveats": CAVEATS,
        "raw_feature_path_hint": f"data/parquet/trends/{entity_id}/features/",
    }
    trends_store.write_score(entity_id, as_of=feat_payload["as_of"], payload=payload)
    return payload
