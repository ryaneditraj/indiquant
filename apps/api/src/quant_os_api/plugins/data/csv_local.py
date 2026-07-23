"""CSV / local directory OHLCV provider — path from env, never hardcoded."""

from __future__ import annotations

import os
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from quant_os_api.config import _repo_root
from quant_os_api.plugins.data.fixture import FixtureDataProvider


class CSVLocalProvider:
    """Load `{root}/{SYMBOL}.csv` with columns ts,open,high,low,close,volume."""

    name = "csv_local"

    def __init__(self) -> None:
        raw = os.getenv("DATA_CSV_ROOT", "data/sample_csv")
        path = Path(raw)
        if not path.is_absolute():
            path = _repo_root() / path
        self.root = path
        self._fixture = FixtureDataProvider()

    def health(self) -> dict[str, Any]:
        exists = self.root.exists()
        files = list(self.root.glob("*.csv")) if exists else []
        return {
            "provider": self.name,
            "status": "ok" if exists else "missing-root",
            "root": str(self.root),
            "csv_files": len(files),
            "fallback": "fixture" if not files else None,
        }

    def get_ohlcv(
        self,
        symbol: str,
        start: date,
        end: date,
        *,
        timeframe: str = "1d",
    ) -> list[dict[str, Any]]:
        _ = timeframe
        path = self.root / f"{symbol.upper()}.csv"
        if not path.exists():
            return self._fixture.get_ohlcv(symbol, start, end, timeframe=timeframe)

        frame = pd.read_csv(path)
        required = {"ts", "open", "high", "low", "close", "volume"}
        if not required.issubset(set(frame.columns)):
            raise ValueError(f"CSV {path} missing columns {required - set(frame.columns)}")
        frame["ts"] = pd.to_datetime(frame["ts"], utc=True)
        start_ts = datetime(start.year, start.month, start.day)
        end_ts = datetime(end.year, end.month, end.day, 23, 59, 59)
        mask = (frame["ts"] >= pd.Timestamp(start_ts, tz="UTC")) & (
            frame["ts"] <= pd.Timestamp(end_ts, tz="UTC")
        )
        subset = frame.loc[mask].copy()
        subset["symbol"] = symbol.upper()
        subset["ts"] = subset["ts"].dt.strftime("%Y-%m-%dT%H:%M:%S%z")
        return subset[["ts", "symbol", "open", "high", "low", "close", "volume"]].to_dict(
            orient="records"
        )
