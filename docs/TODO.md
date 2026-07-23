# TODO — interrupt recovery

Read this after any interruption, then `ROADMAP.md` and `CHANGELOG.md`.

## Status

**v0.1.0 research OS MVP is complete** — discover → backtest → validate → accept/reject → document works offline.

## Next horizon

- [ ] Real NSE vendor HTTP adapter behind `DATA_NSE_API_BASE_URL`
- [ ] LangGraph durable graph + Celery forever-loop with pause/resume UI
- [ ] In-browser notebook kernel (Pyodide or server kernels)
- [ ] Auth / encrypted secrets for multi-user
- [ ] Options architecture plugins
- [ ] Playwright e2e smoke

## Notes for agents

- Branding is placeholder — use `config.app.name`
- Never hardcode provider URLs or API keys
- Prefer evidence, tests, and reproducibility in every PR
- Run `make api-test` after backend changes
