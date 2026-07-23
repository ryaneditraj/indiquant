"""Deterministic fixture provider for tests and offline demos."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from typing import Any


class FixtureDataProvider:
    """Synthetic OHLCV — no network. Enabled by default in config for reproducibility."""

    name = "fixture"

    def health(self) -> dict[str, Any]:
        return {
            "provider": self.name,
            "status": "ok",
            "network": False,
            "message": "Synthetic bars for offline tests",
        }

    def get_ohlcv(
        self,
        symbol: str,
        start: date,
        end: date,
        *,
        timeframe: str = "1d",
    ) -> list[dict[str, Any]]:
        if timeframe != "1d":
            raise ValueError("Fixture provider currently supports timeframe=1d only")
        if end < start:
            raise ValueError("end must be >= start")

        rows: list[dict[str, Any]] = []
        day = start
        # Deterministic pseudo-price from symbol hash
        seed = sum(ord(c) for c in symbol.upper()) % 500
        price = 1000.0 + float(seed)
        while day <= end:
            if day.weekday() < 5:  # Mon–Fri (approx; not exchange calendar yet)
                open_ = price
                high = price * 1.01
                low = price * 0.99
                close = price * (1.0 + ((seed % 7) - 3) * 0.001)
                volume = 100_000 + (seed * 17)
                ts = datetime(day.year, day.month, day.day, tzinfo=UTC)
                rows.append(
                    {
                        "ts": ts.isoformat(),
                        "symbol": symbol.upper(),
                        "open": round(open_, 2),
                        "high": round(high, 2),
                        "low": round(low, 2),
                        "close": round(close, 2),
                        "volume": volume,
                    }
                )
                price = close
            day += timedelta(days=1)
        return rows
