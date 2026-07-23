# TODO — interrupt recovery

Read this after any interruption, then `ROADMAP.md` and `CHANGELOG.md`.

## Status

**v0.2.0** — Forever loop, DuckDB analytics, CSV provider, notebook execute, charts, smoke tests.

## Next horizon

- [ ] Wire real NSE vendor behind `DATA_NSE_API_BASE_URL` (HTTP contract ready)
- [ ] Full LangGraph durable checkpointing
- [ ] Multi-user auth + encrypted secrets vault UI
- [ ] Options architecture plugins
- [ ] Pyodide/in-browser kernel (server REPL exists)
- [ ] CI job that boots API+web and runs Playwright

## Notes for agents

- Branding is placeholder — use `config.app.name`
- Never hardcode provider URLs or API keys
- Prefer evidence, tests, and reproducibility in every PR
- Run `make api-test` after backend changes
