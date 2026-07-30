"""Trends modeling layer — gradient boosting on structured features.

Proxy targets (clearly labeled) until fundamentals / SSS / beat-miss labels
are wired from filings. Artifacts persist under artifacts/trends/.
"""

from __future__ import annotations

import json
import pickle
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np

from quant_os_api.config import _repo_root, get_settings
from quant_os_api.trends import CAVEATS, QUALITY_BADGES
from quant_os_api.trends.features import compute_features
from quant_os_api.trends.fundamentals import load_labels as load_fundamentals_labels
from quant_os_api.trends.score import score_entity
from quant_os_api.trends.universe import entity_config, list_entities

FEATURE_KEYS = [
    "wow_growth",
    "growth_2w",
    "growth_4w",
    "growth_8w",
    "mom_growth",
    "qoq_growth",
    "yoy_seasonal",
    "festival_adjusted_change",
    "ma_4w",
    "ma_8w",
    "trend_slope",
    "trend_acceleration",
    "zscore_1y",
    "volatility",
    "relative_search_share",
    "brand_to_category_ratio",
    "transactional_to_brand_ratio",
    "risk_query_ratio",
    "state_weighted_search_score",
    "core_vs_noncore_spread",
    "search_dispersion",
    "related_query_breadth",
    "corr_satellite",
    "corr_app_rank",
    "divergence_satellite",
    "divergence_pricing",
    "search_confirmation_composite",
    "brand_last",
    "tx_last",
    "risk_last",
]

TASKS = (
    "revenue_growth",
    "sss_proxy",
    "beat_inline_miss",
    "nowcast_momentum",
)


def artifacts_dir() -> Path:
    settings = get_settings()
    root = settings.yaml_config.get("storage", {}).get("artifacts_root", "artifacts")
    path = Path(str(root))
    if not path.is_absolute():
        path = _repo_root() / path
    out = path / "trends"
    out.mkdir(parents=True, exist_ok=True)
    return out


def _safe(v: Any, default: float = 0.0) -> float:
    try:
        if v is None or (isinstance(v, float) and np.isnan(v)):
            return default
        return float(v)
    except (TypeError, ValueError):
        return default


def _vectorize(features: dict[str, Any]) -> np.ndarray:
    return np.asarray([_safe(features.get(k)) for k in FEATURE_KEYS], dtype=float)


def _proxy_labels(score_payload: dict[str, Any], *, rng: np.random.Generator) -> dict[str, Any]:
    """Synthetic labeled targets derived from score regime + noise (demo only)."""
    score = _safe(score_payload.get("search_demand_score"), 50.0)
    regime = str(score_payload.get("regime") or "neutral")
    f = score_payload.get("features") or {}
    mom = _safe(f.get("pre_earn_14d"), _safe(f.get("growth_2w")))
    conf = _safe((score_payload.get("components") or {}).get("signal_quality"), 0.5)

    # Next-quarter revenue growth proxy (%)
    base_rev = (score - 50.0) / 100.0 * 12.0 + mom * 8.0
    rev = base_rev + float(rng.normal(0, 1.5))
    # Same-store sales proxy (%)
    sss = base_rev * 0.55 + _safe(f.get("transactional_to_brand_ratio"), 0.5) * 2.0 + float(rng.normal(0, 1.0))
    # Beat / inline / miss
    if regime == "bullish" or rev > 2.5:
        bim = "beat"
        bim_code = 2
    elif regime == "bearish" or rev < -1.5:
        bim = "miss"
        bim_code = 0
    else:
        bim = "inline"
        bim_code = 1
    # Nowcast current-quarter demand momentum (-1..1)
    nowcast = float(np.clip(mom * 2.0 + (score - 50.0) / 80.0 + rng.normal(0, 0.05), -1.0, 1.0))

    return {
        "revenue_growth": rev,
        "sss_proxy": sss,
        "beat_inline_miss": bim,
        "beat_inline_miss_code": bim_code,
        "nowcast_momentum": nowcast,
        "proxy": True,
        "proxy_note": "Labels are synthetic proxies from score regimes + noise until fundamentals wired.",
        "label_confidence": conf,
    }


def _build_training_rows(entity_ids: list[str] | None = None) -> list[dict[str, Any]]:
    ids = entity_ids or list_entities()
    rows: list[dict[str, Any]] = []
    for eid in ids:
        cfg = entity_config(eid)
        calendar = list(cfg.get("earnings_calendar") or [])
        # Also sample a few as_of dates around today for denser training
        extras = [(datetime.now(UTC).date() - timedelta(days=d)).isoformat() for d in (0, 30, 60, 90)]
        as_ofs = [str(d)[:10] for d in calendar[-8:]] + extras
        for as_of in as_ofs:
            for window in ("90d", "12m"):
                scored = score_entity(eid, as_of=as_of, window=window)
                if not scored.get("ok"):
                    continue
                fund = load_fundamentals_labels(eid, as_of=as_of)
                if fund:
                    bim_code = int(fund.get("beat_inline_miss_code") or 1)
                    labels = {
                        "revenue_growth": float(fund.get("revenue_growth") or 0.0),
                        "sss_proxy": float(fund.get("sss") or fund.get("sss_proxy") or 0.0),
                        "beat_inline_miss": fund.get("beat_inline_miss") or "inline",
                        "beat_inline_miss_code": bim_code,
                        "nowcast_momentum": float(fund.get("nowcast_momentum") or 0.0),
                        "proxy": False,
                        "label_source": "fundamentals",
                        "proxy_note": None,
                        "label_confidence": float(fund.get("label_confidence") or 0.8),
                    }
                else:
                    rng = np.random.default_rng(abs(hash(f"{eid}|{as_of}|{window}")) % (2**32))
                    labels = _proxy_labels(scored, rng=rng)
                    labels["label_source"] = "proxy"
                rows.append(
                    {
                        "entity_id": eid,
                        "as_of": as_of,
                        "window": window,
                        "x": _vectorize(scored["features"]).tolist(),
                        "search_demand_score": scored["search_demand_score"],
                        "regime": scored["regime"],
                        "quality_badge": scored["quality_badge"],
                        **labels,
                    }
                )
    return rows


def _fit_gb_regressor(X: np.ndarray, y: np.ndarray):
    from sklearn.ensemble import GradientBoostingRegressor

    model = GradientBoostingRegressor(
        n_estimators=80,
        max_depth=3,
        learning_rate=0.08,
        subsample=0.9,
        random_state=42,
    )
    model.fit(X, y)
    return model


def _fit_gb_classifier(X: np.ndarray, y: np.ndarray):
    from sklearn.ensemble import GradientBoostingClassifier

    model = GradientBoostingClassifier(
        n_estimators=80,
        max_depth=3,
        learning_rate=0.08,
        subsample=0.9,
        random_state=42,
    )
    model.fit(X, y)
    return model


def _conformal_band(residuals: np.ndarray, pred: float, *, alpha: float = 0.2) -> dict[str, float]:
    """Heuristic split-conformal style absolute residual quantile band."""
    if len(residuals) == 0:
        half = 2.0
    else:
        q = float(np.quantile(np.abs(residuals), 1.0 - alpha))
        half = max(0.5, q)
    return {
        "low": float(pred - half),
        "high": float(pred + half),
        "alpha": alpha,
        "method": "heuristic_absolute_residual_quantile",
    }


def train_models(
    entity_ids: list[str] | None = None,
    *,
    entity_id: str | None = None,
) -> dict[str, Any]:
    """Train GB models on proxy-labeled Trends features; persist under artifacts/trends/."""
    ids = [entity_id] if entity_id else (entity_ids or list_entities())
    # Ensure features exist: scoring will no-op without data
    rows = _build_training_rows(ids)
    if len(rows) < 8:
        return {
            "ok": False,
            "error": "Insufficient training rows — collect Trends for entities first",
            "n_rows": len(rows),
            "proxy_labels": True,
        }

    X = np.asarray([r["x"] for r in rows], dtype=float)
    # Hold out last 20% chronologically-ish for residual calibration
    n = len(rows)
    split = max(4, int(n * 0.8))
    X_tr, X_cal = X[:split], X[split:]
    meta: dict[str, Any] = {
        "trained_at": datetime.now(UTC).isoformat(),
        "n_rows": n,
        "n_train": split,
        "n_cal": n - split,
        "feature_keys": FEATURE_KEYS,
        "entities": sorted({r["entity_id"] for r in rows}),
        "proxy_labels": True,
        "proxy_note": "Targets are synthetic proxies from score regimes + noise until fundamentals wired.",
        "label_source": (
            "fundamentals"
            if any(r.get("label_source") == "fundamentals" for r in rows)
            else "proxy"
        ),
        "label_sources_used": sorted({str(r.get("label_source") or "proxy") for r in rows}),
        "is_absolute_volume": False,
        "caveats": CAVEATS,
        "tasks": {},
    }

    artifacts = artifacts_dir()
    models_path = artifacts / "models.pkl"
    models: dict[str, Any] = {}

    # Revenue growth regression
    y_rev = np.asarray([r["revenue_growth"] for r in rows], dtype=float)
    reg_rev = _fit_gb_regressor(X_tr, y_rev[:split])
    pred_cal = reg_rev.predict(X_cal) if len(X_cal) else np.array([])
    resid = y_rev[split:] - pred_cal if len(X_cal) else np.array([])
    models["revenue_growth"] = {"kind": "regressor", "model": reg_rev, "residuals": resid.tolist()}
    meta["tasks"]["revenue_growth"] = {
        "type": "regression",
        "train_mae": float(np.mean(np.abs(y_rev[:split] - reg_rev.predict(X_tr)))),
        "cal_mae": float(np.mean(np.abs(resid))) if len(resid) else None,
    }

    # SSS proxy regression
    y_sss = np.asarray([r["sss_proxy"] for r in rows], dtype=float)
    reg_sss = _fit_gb_regressor(X_tr, y_sss[:split])
    pred_cal = reg_sss.predict(X_cal) if len(X_cal) else np.array([])
    resid = y_sss[split:] - pred_cal if len(X_cal) else np.array([])
    models["sss_proxy"] = {"kind": "regressor", "model": reg_sss, "residuals": resid.tolist()}
    meta["tasks"]["sss_proxy"] = {
        "type": "regression",
        "train_mae": float(np.mean(np.abs(y_sss[:split] - reg_sss.predict(X_tr)))),
        "cal_mae": float(np.mean(np.abs(resid))) if len(resid) else None,
    }

    # Beat / inline / miss classification
    y_cls = np.asarray([r["beat_inline_miss_code"] for r in rows], dtype=int)
    # Need at least 2 classes present in train
    if len(set(y_cls[:split].tolist())) >= 2:
        clf = _fit_gb_classifier(X_tr, y_cls[:split])
        acc = float((clf.predict(X_tr) == y_cls[:split]).mean())
        models["beat_inline_miss"] = {
            "kind": "classifier",
            "model": clf,
            "label_map": {0: "miss", 1: "inline", 2: "beat"},
        }
        meta["tasks"]["beat_inline_miss"] = {"type": "classification", "train_accuracy": acc}
    else:
        meta["tasks"]["beat_inline_miss"] = {
            "type": "classification",
            "skipped": True,
            "reason": "Need ≥2 classes in training split",
        }

    # Nowcast momentum regression
    y_now = np.asarray([r["nowcast_momentum"] for r in rows], dtype=float)
    reg_now = _fit_gb_regressor(X_tr, y_now[:split])
    pred_cal = reg_now.predict(X_cal) if len(X_cal) else np.array([])
    resid = y_now[split:] - pred_cal if len(X_cal) else np.array([])
    models["nowcast_momentum"] = {"kind": "regressor", "model": reg_now, "residuals": resid.tolist()}
    meta["tasks"]["nowcast_momentum"] = {
        "type": "regression",
        "train_mae": float(np.mean(np.abs(y_now[:split] - reg_now.predict(X_tr)))),
        "cal_mae": float(np.mean(np.abs(resid))) if len(resid) else None,
    }

    with models_path.open("wb") as fh:
        pickle.dump({"models": models, "meta": meta}, fh)
    (artifacts / "train_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    # Persist a small training frame for audit (no pickle in JSON)
    sample = [
        {
            "entity_id": r["entity_id"],
            "as_of": r["as_of"],
            "window": r["window"],
            "revenue_growth": r["revenue_growth"],
            "sss_proxy": r["sss_proxy"],
            "beat_inline_miss": r["beat_inline_miss"],
            "nowcast_momentum": r["nowcast_momentum"],
            "search_demand_score": r["search_demand_score"],
            "quality_badge": r["quality_badge"],
        }
        for r in rows[:200]
    ]
    (artifacts / "training_sample.json").write_text(json.dumps(sample, indent=2), encoding="utf-8")

    return {"ok": True, "artifact_dir": str(artifacts), "meta": meta}


def _load_models() -> dict[str, Any] | None:
    path = artifacts_dir() / "models.pkl"
    if not path.exists():
        return None
    with path.open("rb") as fh:
        return pickle.load(fh)  # noqa: S301 — local trusted artifact


def predict_entity(entity_id: str, *, window: str = "90d", as_of: str | None = None) -> dict[str, Any]:
    scored = score_entity(entity_id, as_of=as_of, window=window)
    if not scored.get("ok"):
        return {"ok": False, "entity_id": entity_id, "error": scored.get("error")}

    bundle = _load_models()
    if bundle is None:
        return {
            "ok": False,
            "entity_id": entity_id,
            "error": "No trained models — POST /api/v1/trends/models/train first",
        }

    models = bundle["models"]
    meta = bundle["meta"]
    x = _vectorize(scored["features"]).reshape(1, -1)
    badge = scored.get("quality_badge", "medium")

    out: dict[str, Any] = {
        "ok": True,
        "entity_id": entity_id,
        "label": scored.get("label"),
        "ticker": scored.get("ticker"),
        "as_of": scored["as_of"],
        "window": window,
        "quality_badge": badge,
        "quality_badges_allowed": list(QUALITY_BADGES),
        "proxy_labels": True,
        "proxy_note": meta.get("proxy_note"),
        "label_source": meta.get("label_source") or "proxy",
        "is_absolute_volume": False,
        "caveats": CAVEATS,
        "predictions": {},
    }

    if "revenue_growth" in models:
        pred = float(models["revenue_growth"]["model"].predict(x)[0])
        band = _conformal_band(np.asarray(models["revenue_growth"]["residuals"], dtype=float), pred)
        out["predictions"]["revenue_growth"] = {
            "value": round(pred, 3),
            "unit": "pct_proxy",
            "confidence_interval": band,
        }
    if "sss_proxy" in models:
        pred = float(models["sss_proxy"]["model"].predict(x)[0])
        band = _conformal_band(np.asarray(models["sss_proxy"]["residuals"], dtype=float), pred)
        out["predictions"]["sss_proxy"] = {
            "value": round(pred, 3),
            "unit": "pct_proxy",
            "confidence_interval": band,
        }
    if "beat_inline_miss" in models:
        clf = models["beat_inline_miss"]["model"]
        label_map = models["beat_inline_miss"]["label_map"]
        code = int(clf.predict(x)[0])
        proba = None
        if hasattr(clf, "predict_proba"):
            raw = clf.predict_proba(x)[0]
            classes = [int(c) for c in clf.classes_]
            proba = {label_map.get(c, str(c)): round(float(p), 4) for c, p in zip(classes, raw, strict=False)}
        out["predictions"]["beat_inline_miss"] = {
            "class": label_map.get(code, str(code)),
            "probabilities": proba,
        }
    if "nowcast_momentum" in models:
        pred = float(models["nowcast_momentum"]["model"].predict(x)[0])
        band = _conformal_band(np.asarray(models["nowcast_momentum"]["residuals"], dtype=float), pred, alpha=0.25)
        out["predictions"]["nowcast_momentum"] = {
            "value": round(float(np.clip(pred, -1, 1)), 4),
            "unit": "momentum_-1_to_1",
            "confidence_interval": {
                "low": round(float(np.clip(band["low"], -1, 1)), 4),
                "high": round(float(np.clip(band["high"], -1, 1)), 4),
                "alpha": band["alpha"],
                "method": band["method"],
            },
        }

    # Ranking signal: higher predicted revenue growth + beat prob
    rank_score = _safe(out["predictions"].get("revenue_growth", {}).get("value"))
    beat_p = 0.0
    bim = out["predictions"].get("beat_inline_miss") or {}
    if bim.get("probabilities"):
        beat_p = float(bim["probabilities"].get("beat") or 0.0)
    out["ranking_score"] = round(rank_score + 5.0 * beat_p, 4)
    out["search_demand_score"] = scored["search_demand_score"]
    out["regime"] = scored["regime"]
    return out


def nowcast_entity(entity_id: str, *, window: str = "90d") -> dict[str, Any]:
    pred = predict_entity(entity_id, window=window)
    if not pred.get("ok"):
        return pred
    nc = (pred.get("predictions") or {}).get("nowcast_momentum") or {}
    return {
        "ok": True,
        "entity_id": entity_id,
        "label": pred.get("label"),
        "as_of": pred.get("as_of"),
        "quality_badge": pred.get("quality_badge"),
        "nowcast_momentum": nc.get("value"),
        "confidence_interval": nc.get("confidence_interval"),
        "search_demand_score": pred.get("search_demand_score"),
        "regime": pred.get("regime"),
        "proxy_labels": True,
        "proxy_note": pred.get("proxy_note"),
        "is_absolute_volume": False,
        "caveats": CAVEATS,
    }


_QUALITY_TIER = {"high": 0, "medium": 1, "low": 2, "unreliable": 3}


def _side_hint(*, rank: int, n: int, quality_badge: str | None) -> str:
    """Tertile long/short labels — withheld for unreliable samples."""
    if quality_badge == "unreliable":
        return "watch"
    if n <= 0:
        return "neutral"
    top = max(1, n // 3)
    bottom = max(1, n // 3)
    if rank <= top:
        return "long"
    if rank > n - bottom:
        return "short"
    return "neutral"


def rank_entities(
    entity_ids: list[str] | None = None,
    *,
    window: str = "90d",
) -> dict[str, Any]:
    ids = entity_ids or list_entities()
    rows: list[dict[str, Any]] = []
    for eid in ids:
        # Skip unknown / empty entities without aborting the whole ranking
        try:
            feat = compute_features(eid, window=window)
        except KeyError as exc:
            rows.append(
                {
                    "entity_id": eid,
                    "ok": False,
                    "error": str(exc),
                    "ranking_score": None,
                    "ranking_method": None,
                }
            )
            continue
        if not feat.get("ok"):
            rows.append(
                {
                    "entity_id": eid,
                    "ok": False,
                    "error": feat.get("error"),
                    "ranking_score": None,
                    "ranking_method": None,
                }
            )
            continue
        pred = predict_entity(eid, window=window)
        if not pred.get("ok"):
            # Fallback ranking from search demand score alone
            scored = score_entity(eid, window=window)
            rows.append(
                {
                    "entity_id": eid,
                    "ok": True,
                    "label": scored.get("label"),
                    "ticker": scored.get("ticker"),
                    "ranking_score": scored.get("search_demand_score"),
                    "search_demand_score": scored.get("search_demand_score"),
                    "quality_badge": scored.get("quality_badge"),
                    "regime": scored.get("regime"),
                    "model_ready": False,
                    "ranking_method": "demand_fallback",
                    "is_absolute_volume": False,
                }
            )
            continue
        rows.append(
            {
                "entity_id": eid,
                "ok": True,
                "label": pred.get("label"),
                "ticker": pred.get("ticker"),
                "ranking_score": pred.get("ranking_score"),
                "search_demand_score": pred.get("search_demand_score"),
                "quality_badge": pred.get("quality_badge"),
                "regime": pred.get("regime"),
                "predictions": pred.get("predictions"),
                "model_ready": True,
                "ranking_method": "model",
                "proxy_labels": True,
                "is_absolute_volume": False,
            }
        )
    # Score desc → quality tier asc (high first) → demand desc as tie-break
    ranked = sorted(
        [r for r in rows if r.get("ranking_score") is not None],
        key=lambda r: (
            -float(r["ranking_score"]),
            _QUALITY_TIER.get(str(r.get("quality_badge") or "medium"), 9),
            -float(r.get("search_demand_score") or 0.0),
        ),
    )
    for i, r in enumerate(ranked, start=1):
        r["rank"] = i
        r["side_hint"] = _side_hint(
            rank=i,
            n=len(ranked),
            quality_badge=r.get("quality_badge"),
        )
    methods = {r.get("ranking_method") for r in ranked if r.get("ranking_method")}
    out: dict[str, Any] = {
        "ok": True,
        "window": window,
        "n": len(ranked),
        "rankings": ranked,
        "failed": [r for r in rows if not r.get("ok")],
        "proxy_labels": True,
        "proxy_note": (
            "Ranking uses proxy-trained models and/or Search Demand Score until fundamentals "
            "wired. side_hint is a relative tertile label — not a trade recommendation. "
            "Unreliable quality → side_hint=watch."
        ),
        "ranking_methods_used": sorted(m for m in methods if m),
        "is_absolute_volume": False,
        "caveats": CAVEATS,
    }
    if len(ranked) == 0:
        out["empty_state"] = True
        out["next_steps"] = [
            "make trends-demo  # fixture offline seed for dmart + trent",
            "Open /trends → Multi-entity ranking → Refresh",
            "Optional: make trends-train for proxy model ranking",
            "Export: GET /api/v1/trends/comparison?format=csv",
        ]
    return out
