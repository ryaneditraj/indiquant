"""Data provider plugin protocol (pandas-free in Phase 0; adapters may use DataFrames later)."""

from __future__ import annotations

from datetime import date
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class DataProvider(Protocol):
    """Market data adapter. Implementations are loaded from config.yaml module paths."""

    name: str

    def health(self) -> dict[str, Any]:
        """Return provider readiness and last-success metadata."""
        ...

    def get_ohlcv(
        self,
        symbol: str,
        start: date,
        end: date,
        *,
        timeframe: str = "1d",
    ) -> list[dict[str, Any]]:
        """Return OHLCV rows: ts, open, high, low, close, volume."""
        ...
