"""Seed sample CSV datasets for offline Indian-market demos."""

from __future__ import annotations

from datetime import date

import pandas as pd

from quant_os_api.config import _repo_root
from quant_os_api.plugins.data.fixture import FixtureDataProvider
from quant_os_api.services import parquet_store


def seed_sample_data(symbols: list[str] | None = None) -> dict:
    symbols = symbols or ["RELIANCE", "TCS", "INFY", "NIFTY"]
    provider = FixtureDataProvider()
    csv_root = _repo_root() / "data" / "sample_csv"
    csv_root.mkdir(parents=True, exist_ok=True)
    written = []
    for symbol in symbols:
        rows = provider.get_ohlcv(symbol, date(2020, 1, 1), date(2025, 12, 31))
        frame = pd.DataFrame(rows)
        csv_path = csv_root / f"{symbol}.csv"
        frame.to_csv(csv_path, index=False)
        parquet_store.write_ohlcv(symbol, rows)
        written.append({"symbol": symbol, "csv": str(csv_path), "rows": len(rows)})
    return {"seeded": written, "csv_root": str(csv_root)}


if __name__ == "__main__":
    print(seed_sample_data())
