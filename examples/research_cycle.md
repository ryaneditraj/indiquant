# Example: research cycle offline

```bash
curl -s -X POST http://localhost:8000/api/v1/ai/cycle \
  -H 'Content-Type: application/json' \
  -d '{
    "symbol": "RELIANCE",
    "lookback_days": 365,
    "seed": 42,
    "provider": "fixture",
    "persist": true
  }' | python -m json.tool
```

Hypothesis is generated first; strategy code follows; validation gates accept or reject with reasons and an experiment UUID.
