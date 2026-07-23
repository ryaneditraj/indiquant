"""Configurable NSE historical adapter.

Fetches OHLCV from DATA_NSE_API_BASE_URL using a documented URL template.
If the base URL is unset, falls back to the fixture provider (offline-safe).
"""

from __future__ import annotations

import os
from datetime import date
from typing import Any
from urllib.parse import quote

import httpx

from quant_os_api.plugins.data.fixture import FixtureDataProvider


class NSEHistoricalProvider:
    """HTTP OHLCV provider for NSE symbols.

    Contract (configurable):
      GET {base}/{symbol}?start=YYYY-MM-DD&end=YYYY-MM-DD&timeframe=1d
      JSON: { "bars": [ {ts, open, high, low, close, volume}, ... ] }
         or a bare list of bar objects.
    """

    name = "nse_historical"

    def __init__(self) -> None:
        self.base_url = os.getenv("DATA_NSE_API_BASE_URL", "").rstrip("/")
        self.api_key = os.getenv("DATA_NSE_API_KEY", "")
        self._fixture = FixtureDataProvider()

    def health(self) -> dict[str, Any]:
        if not self.base_url:
            return {
                "provider": self.name,
                "status": "degraded",
                "mode": "fixture-fallback",
                "message": "DATA_NSE_API_BASE_URL unset — using synthetic fixture bars",
            }
        return {
            "provider": self.name,
            "status": "ok",
            "mode": "http",
            "base_url": self.base_url,
            "has_api_key": bool(self.api_key),
        }

    def get_ohlcv(
        self,
        symbol: str,
        start: date,
        end: date,
        *,
        timeframe: str = "1d",
    ) -> list[dict[str, Any]]:
        if not self.base_url:
            return self._fixture.get_ohlcv(symbol, start, end, timeframe=timeframe)

        url = f"{self.base_url}/{quote(symbol.upper())}"
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        params = {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "timeframe": timeframe,
            "exchange": "NSE",
        }
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, params=params, headers=headers)
            response.raise_for_status()
            payload = response.json()

        bars = payload.get("bars", payload) if isinstance(payload, dict) else payload
        if not isinstance(bars, list):
            raise ValueError("NSE provider response must be a list or {bars: [...]}")
        rows: list[dict[str, Any]] = []
        for bar in bars:
            if not isinstance(bar, dict):
                continue
            rows.append(
                {
                    "ts": bar["ts"],
                    "symbol": symbol.upper(),
                    "open": float(bar["open"]),
                    "high": float(bar["high"]),
                    "low": float(bar["low"]),
                    "close": float(bar["close"]),
                    "volume": float(bar.get("volume", 0)),
                }
            )
        return rows
