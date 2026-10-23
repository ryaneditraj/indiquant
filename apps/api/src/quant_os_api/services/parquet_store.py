"""Parquet OHLCV store — path rooted in config storage.parquet_root."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from quant_os_api.config import get_settings
from quant_os_api.safe_ids import UnsafePathError, ensure_within, safe_symbol, safe_timeframe


def parquet_root() -> Path:
    settings = get_settings()
    root = settings.yaml_config.get("storage", {}).get("parquet_root", "data/parquet")
    path = Path(str(root))
    if not path.is_absolute():
        # Resolve from monorepo root (config.py parents[4])
        from quant_os_api.config import _repo_root

        path = _repo_root() / path
    path.mkdir(parents=True, exist_ok=True)
    return path


def symbol_path(symbol: str, timeframe: str = "1d") -> Path:
    safe = safe_symbol(symbol)
    tf = safe_timeframe(timeframe)
    root = parquet_root()
    directory = root / safe
    path = ensure_within(root, directory / f"{tf}.parquet")
    directory.mkdir(parents=True, exist_ok=True)
    return path


def write_ohlcv(symbol: str, rows: list[dict[str, Any]], *, timeframe: str = "1d") -> Path:
    if not rows:
        raise ValueError("No rows to write")
    frame = pd.DataFrame(rows)
    path = symbol_path(symbol, timeframe)
    if path.exists():
        existing = pd.read_parquet(path)
        frame = (
            pd.concat([existing, frame], ignore_index=True)
            .drop_duplicates(subset=["ts"], keep="last")
            .sort_values("ts")
        )
    else:
        frame = frame.sort_values("ts")
    frame.to_parquet(path, index=False)
    return path


def read_ohlcv(symbol: str, *, timeframe: str = "1d") -> pd.DataFrame:
    path = symbol_path(symbol, timeframe)
    if not path.exists():
        return pd.DataFrame(columns=["ts", "symbol", "open", "high", "low", "close", "volume"])
    return pd.read_parquet(path)


def list_datasets() -> list[dict[str, Any]]:
    root = parquet_root()
    datasets: list[dict[str, Any]] = []
    for symbol_dir in sorted(root.iterdir() if root.exists() else []):
        if not symbol_dir.is_dir():
            continue
        # Skip alt-data namespaces (Trends lives under parquet/trends/)
        if symbol_dir.name.lower() in {"trends"}:
            continue
        try:
            safe_symbol(symbol_dir.name)
        except UnsafePathError:
            continue
        for file in sorted(symbol_dir.glob("*.parquet")):
            try:
                safe_timeframe(file.stem)
            except UnsafePathError:
                continue
            frame = pd.read_parquet(file)
            timeframe = file.stem
            freshness = None
            if not frame.empty and "ts" in frame.columns:
                freshness = str(frame["ts"].max())
            datasets.append(
                {
                    "symbol": symbol_dir.name,
                    "timeframe": timeframe,
                    "rows": int(len(frame)),
                    "path": str(file.relative_to(root.parent.parent))
                    if root.parent.parent.exists()
                    else str(file),
                    "freshness": freshness,
                    "schema": list(frame.columns),
                    "updated_at": datetime.fromtimestamp(
                        file.stat().st_mtime, tz=UTC
                    ).isoformat(),
                }
            )
    return datasets
