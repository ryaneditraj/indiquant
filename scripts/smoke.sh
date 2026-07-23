#!/usr/bin/env bash
# API smoke — requires API on :8000
set -euo pipefail
BASE="${API_BASE:-http://localhost:8000}"

echo "health"
curl -sf "$BASE/api/v1/health" | grep -q '"status":"ok"'

echo "seed"
curl -sf -X POST "$BASE/api/v1/admin/seed" >/dev/null

echo "cycle"
curl -sf -X POST "$BASE/api/v1/ai/cycle" \
  -H 'Content-Type: application/json' \
  -d '{"symbol":"RELIANCE","provider":"fixture","persist":true,"lookback_days":90}' \
  | grep -q experiment

echo "loop start/stop"
curl -sf -X POST "$BASE/api/v1/ai/loop/start" \
  -H 'Content-Type: application/json' \
  -d '{"symbols":["TCS"],"provider":"fixture","max_cycles":1,"interval_seconds":0.5}' >/dev/null
sleep 2
curl -sf -X POST "$BASE/api/v1/ai/loop/stop" >/dev/null

echo "OK"
