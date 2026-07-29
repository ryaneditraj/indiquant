#!/usr/bin/env bash
# Weekly Google Trends collect for all configured entities (cron-friendly).
# Example crontab (Sunday 02:30 Asia/Kolkata):
#   30 2 * * 0 cd /path/to/quant-os && bash scripts/trends_weekly.sh >> logs/trends_cron.log 2>&1
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/apps/api"
# shellcheck disable=SC1091
source .venv/bin/activate
export QUANT_OS_CONFIG_PATH="${QUANT_OS_CONFIG_PATH:-$ROOT/config.yaml}"
PROVIDER="${TRENDS_PROVIDER:-fixture}"
python - <<PY
from quant_os_api.trends.collector import collect_entity
from quant_os_api.trends.score import score_entity
from quant_os_api.trends.universe import list_entities
import json, os
provider = os.environ.get("TRENDS_PROVIDER", "fixture")
out = []
for eid in list_entities():
    c = collect_entity(eid, provider=provider)
    s = score_entity(eid)
    out.append({
        "entity_id": eid,
        "run_id": c.get("run_id"),
        "score": s.get("search_demand_score"),
        "quality_badge": s.get("quality_badge"),
        "is_absolute_volume": False,
    })
print(json.dumps({"ok": True, "n": len(out), "results": out}, indent=2))
PY
