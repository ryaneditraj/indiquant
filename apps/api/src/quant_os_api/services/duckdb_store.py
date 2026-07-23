"""DuckDB analytics over Parquet OHLCV."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from quant_os_api.config import _repo_root, get_settings
from quant_os_api.services import parquet_store


def duckdb_path() -> Path:
    settings = get_settings()
    raw = settings.yaml_config.get("duckdb", {}).get("path", "data/analytics/quant_os.duckdb")
    path = Path(str(raw))
    if not path.is_absolute():
        path = _repo_root() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def sync_parquet_to_duckdb() -> dict[str, Any]:
    """Register / refresh parquet files into DuckDB views."""
    try:
        import duckdb
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("duckdb package not installed") from exc

    datasets = parquet_store.list_datasets()
    con = duckdb.connect(str(duckdb_path()))
    registered = []
    try:
        for ds in datasets:
            symbol = str(ds["symbol"])
            timeframe = str(ds["timeframe"])
            path = parquet_store.symbol_path(symbol, timeframe)
            view = f"ohlcv_{symbol.lower()}_{timeframe}"
            # DuckDB disallows prepared params in CREATE VIEW — escape path literally
            escaped = str(path).replace("'", "''")
            con.execute(
                f"CREATE OR REPLACE VIEW {view} AS SELECT * FROM read_parquet('{escaped}')"
            )
            registered.append(view)
        summary = con.execute(
            """
            SELECT ? AS dataset_count, ? AS duckdb_path
            """,
            [len(registered), str(duckdb_path())],
        ).fetchone()
    finally:
        con.close()
    return {
        "registered_views": registered,
        "dataset_count": int(summary[0]) if summary else len(registered),
        "path": str(duckdb_path()),
    }


def query_duckdb(sql: str, *, max_rows: int = 500) -> dict[str, Any]:
    """Run read-only analytics SQL. Only SELECT allowed."""
    stripped = sql.strip().lower()
    if not stripped.startswith("select"):
        raise ValueError("Only SELECT queries are allowed")
    forbidden = ("insert", "update", "delete", "drop", "alter", "attach", "copy", "pragma")
    if any(f" {token} " in f" {stripped} " for token in forbidden):
        raise ValueError("Mutating SQL is not allowed")

    import duckdb

    con = duckdb.connect(str(duckdb_path()), read_only=True)
    try:
        frame = con.execute(sql).fetchdf()
    finally:
        con.close()
    if len(frame) > max_rows:
        frame = frame.head(max_rows)
    return {
        "columns": list(frame.columns),
        "rows": frame.to_dict(orient="records"),
        "n": len(frame),
    }
