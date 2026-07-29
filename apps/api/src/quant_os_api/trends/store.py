"""Point-in-time Trends parquet store — raw and transformed layers kept separate."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd

from quant_os_api.config import _repo_root, get_settings


def trends_root() -> Path:
    settings = get_settings()
    root = settings.yaml_config.get("storage", {}).get("parquet_root", "data/parquet")
    path = Path(str(root))
    if not path.is_absolute():
        path = _repo_root() / path
    out = path / "trends"
    out.mkdir(parents=True, exist_ok=True)
    return out


def entity_dir(entity_id: str) -> Path:
    d = trends_root() / entity_id.lower()
    d.mkdir(parents=True, exist_ok=True)
    (d / "raw").mkdir(exist_ok=True)
    (d / "features").mkdir(exist_ok=True)
    (d / "runs").mkdir(exist_ok=True)
    return d


def new_run_id() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]


def write_raw_interest(
    entity_id: str,
    *,
    run_id: str,
    rows: list[dict[str, Any]],
) -> Path:
    """Append interest-over-time raw observations."""
    if not rows:
        raise ValueError("No interest rows")
    frame = pd.DataFrame(rows)
    path = entity_dir(entity_id) / "raw" / "interest_over_time.parquet"
    if path.exists():
        existing = pd.read_parquet(path)
        frame = pd.concat([existing, frame], ignore_index=True)
    frame.to_parquet(path, index=False)
    _append_run_manifest(entity_id, run_id, channel="interest_over_time", rows=len(rows))
    return path


def write_raw_region(entity_id: str, *, run_id: str, rows: list[dict[str, Any]]) -> Path:
    if not rows:
        raise ValueError("No region rows")
    frame = pd.DataFrame(rows)
    path = entity_dir(entity_id) / "raw" / "interest_by_region.parquet"
    if path.exists():
        existing = pd.read_parquet(path)
        frame = pd.concat([existing, frame], ignore_index=True)
    frame.to_parquet(path, index=False)
    _append_run_manifest(entity_id, run_id, channel="interest_by_region", rows=len(rows))
    return path


def write_raw_related(entity_id: str, *, run_id: str, rows: list[dict[str, Any]]) -> Path:
    if not rows:
        raise ValueError("No related rows")
    frame = pd.DataFrame(rows)
    path = entity_dir(entity_id) / "raw" / "related_queries.parquet"
    if path.exists():
        existing = pd.read_parquet(path)
        frame = pd.concat([existing, frame], ignore_index=True)
    frame.to_parquet(path, index=False)
    _append_run_manifest(entity_id, run_id, channel="related_queries", rows=len(rows))
    return path


def write_features(entity_id: str, *, as_of: str, payload: dict[str, Any]) -> Path:
    path = entity_dir(entity_id) / "features" / f"{as_of}.json"
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return path


def write_score(entity_id: str, *, as_of: str, payload: dict[str, Any]) -> Path:
    path = entity_dir(entity_id) / "features" / f"score_{as_of}.json"
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return path


def _append_run_manifest(entity_id: str, run_id: str, *, channel: str, rows: int) -> None:
    path = entity_dir(entity_id) / "runs" / f"{run_id}.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = {
            "run_id": run_id,
            "entity_id": entity_id,
            "collected_at": datetime.now(UTC).isoformat(),
            "channels": {},
        }
    data["channels"][channel] = {"rows": rows, "written_at": datetime.now(UTC).isoformat()}
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def read_interest(
    entity_id: str,
    *,
    as_of: str | None = None,
    query_group: str | None = None,
) -> pd.DataFrame:
    path = entity_dir(entity_id) / "raw" / "interest_over_time.parquet"
    if not path.exists():
        return pd.DataFrame()
    frame = pd.read_parquet(path)
    if as_of:
        as_of_day = as_of[:10]
        # True PIT: only pulls completed by as_of. Fixture series also truncates
        # observation dates so pre-earnings backtests never see future points.
        if "collected_at" in frame.columns:
            pulled = frame[frame["collected_at"].astype(str) <= as_of]
            if pulled.empty and "date" in frame.columns:
                frame = frame[frame["date"].astype(str) <= as_of_day]
            else:
                frame = pulled
                if "date" in frame.columns:
                    frame = frame[frame["date"].astype(str) <= as_of_day]
        elif "date" in frame.columns:
            frame = frame[frame["date"].astype(str) <= as_of_day]
    if query_group and "query_group" in frame.columns:
        frame = frame[frame["query_group"] == query_group]
    return frame


def read_regions(entity_id: str, *, as_of: str | None = None) -> pd.DataFrame:
    path = entity_dir(entity_id) / "raw" / "interest_by_region.parquet"
    if not path.exists():
        return pd.DataFrame()
    frame = pd.read_parquet(path)
    if as_of and "collected_at" in frame.columns:
        pulled = frame[frame["collected_at"].astype(str) <= as_of]
        # Regional snapshots are as-of the pull; for fixture backtests keep latest
        # snapshot if no pull existed yet before as_of (synthetic history).
        frame = pulled if not pulled.empty else frame
    return frame


def read_related(entity_id: str, *, as_of: str | None = None) -> pd.DataFrame:
    path = entity_dir(entity_id) / "raw" / "related_queries.parquet"
    if not path.exists():
        return pd.DataFrame()
    frame = pd.read_parquet(path)
    if as_of and "collected_at" in frame.columns:
        pulled = frame[frame["collected_at"].astype(str) <= as_of]
        frame = pulled if not pulled.empty else frame
    return frame


def latest_score(entity_id: str) -> dict[str, Any] | None:
    feats = entity_dir(entity_id) / "features"
    scores = sorted(feats.glob("score_*.json"))
    if not scores:
        return None
    return json.loads(scores[-1].read_text(encoding="utf-8"))


def list_runs(entity_id: str) -> list[dict[str, Any]]:
    runs_dir = entity_dir(entity_id) / "runs"
    out: list[dict[str, Any]] = []
    for path in sorted(runs_dir.glob("*.json"), reverse=True):
        out.append(json.loads(path.read_text(encoding="utf-8")))
    return out


def inventory(entity_id: str) -> dict[str, Any]:
    root = entity_dir(entity_id)
    interest = root / "raw" / "interest_over_time.parquet"
    region = root / "raw" / "interest_by_region.parquet"
    related = root / "raw" / "related_queries.parquet"

    def _rows(p: Path) -> int:
        if not p.exists():
            return 0
        return int(len(pd.read_parquet(p)))

    return {
        "entity_id": entity_id,
        "interest_rows": _rows(interest),
        "region_rows": _rows(region),
        "related_rows": _rows(related),
        "runs": len(list((root / "runs").glob("*.json"))),
        "scores": len(list((root / "features").glob("score_*.json"))),
    }
