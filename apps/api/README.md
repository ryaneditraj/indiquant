# Indiquant API

FastAPI backend for **Indiquant** — Money Radar's evidence-first quant research OS (Thugir Group).

```bash
pip install -e ".[dev]"
QUANT_OS_CONFIG_PATH=../../config.yaml uvicorn quant_os_api.main:app --reload --port 8000
```

- OpenAPI: http://localhost:8000/docs  
- Health: `GET /api/v1/health`  
- License: PolyForm Noncommercial 1.0.0 (see repo root)
