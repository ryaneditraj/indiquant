#!/usr/bin/env bash
# Offline Trends demo: fixture collect + score for dmart + trent.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/apps/api"
# shellcheck disable=SC1091
. .venv/bin/activate
export QUANT_OS_CONFIG_PATH="$ROOT/config.yaml"
python - <<'PY'
from quant_os_api.trends.collector import collect_entity
from quant_os_api.trends.score import score_entity
from quant_os_api.trends.modeling import rank_entities

out = []
for e in ("dmart", "trent"):
    c = collect_entity(e, provider="fixture")
    s = score_entity(e)
    out.append(
        {
            "entity": e,
            "run": c.get("run_id"),
            "score": s.get("search_demand_score"),
            "badge": s.get("quality_badge"),
            "ok": s.get("ok"),
        }
    )
ranked = rank_entities(["dmart", "trent"])
print({"collected": out, "n_ranked": ranked.get("n"), "is_absolute_volume": False})
print("Open http://localhost:3000/trends after make api-dev && make web-dev")
PY
