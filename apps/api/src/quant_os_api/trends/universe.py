"""Configurable Trends query universe (multi-entity Phase 2)."""

from __future__ import annotations

from typing import Any

from quant_os_api.config import get_settings

QUERY_TYPES = ("brand", "transactional", "category", "competitor", "risk")


def trends_config() -> dict[str, Any]:
    return dict(get_settings().yaml_config.get("google_trends", {}) or {})


def list_entities() -> list[str]:
    return sorted((trends_config().get("entities") or {}).keys())


def entity_config(entity_id: str = "dmart") -> dict[str, Any]:
    entities = trends_config().get("entities") or {}
    if entity_id not in entities:
        raise KeyError(f"Unknown trends entity: {entity_id}")
    return dict(entities[entity_id])


def iter_queries(entity_id: str = "dmart") -> list[dict[str, Any]]:
    """Flatten tagged queries for an entity."""
    cfg = entity_config(entity_id)
    rows: list[dict[str, Any]] = []
    for qtype in QUERY_TYPES:
        for item in cfg.get("queries", {}).get(qtype, []) or []:
            rows.append(
                {
                    "entity_id": entity_id,
                    "query_type": qtype,
                    "term": str(item["term"]),
                    "kind": str(item.get("kind", "search_term")),
                }
            )
    return rows


def anchor_terms(entity_id: str = "dmart") -> list[str]:
    anchors = trends_config().get("anchors") or {}
    terms: list[str] = []
    terms.extend(str(t) for t in anchors.get("fixed", []) or [])
    terms.extend(str(t) for t in anchors.get("category", []) or [])
    if anchors.get("competitor_basket"):
        cfg = entity_config(entity_id)
        for item in cfg.get("queries", {}).get("competitor", []) or []:
            terms.append(str(item["term"]))
    # de-dupe preserve order
    seen: set[str] = set()
    out: list[str] = []
    for t in terms:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def comparison_groups(entity_id: str = "dmart") -> list[dict[str, Any]]:
    """Shared-request groups so relative normalization context is preserved."""
    cfg = entity_config(entity_id)
    groups: list[dict[str, Any]] = []
    brand = [q["term"] for q in cfg.get("queries", {}).get("brand", [])]
    transactional = [q["term"] for q in cfg.get("queries", {}).get("transactional", [])]
    competitor = [q["term"] for q in cfg.get("queries", {}).get("competitor", [])]
    risk = [q["term"] for q in cfg.get("queries", {}).get("risk", [])]
    category = [q["term"] for q in cfg.get("queries", {}).get("category", [])]
    anchors = anchor_terms(entity_id)[:2]

    if brand:
        groups.append({"group_id": "brand_vs_anchor", "terms": brand[:4] + anchors[:1], "role": "brand"})
    if transactional:
        groups.append(
            {
                "group_id": "tx_vs_brand",
                "terms": transactional[:3] + brand[:1] + anchors[:1],
                "role": "transactional",
            }
        )
    if competitor and brand:
        groups.append(
            {
                "group_id": "competitor_basket",
                "terms": [brand[0]] + competitor[:4],
                "role": "competitor",
            }
        )
    if risk and brand:
        groups.append({"group_id": "risk_vs_brand", "terms": risk[:3] + brand[:1], "role": "risk"})
    if category and brand:
        groups.append(
            {
                "group_id": "brand_vs_category",
                "terms": [brand[0]] + category[:3],
                "role": "category",
            }
        )
    return groups
