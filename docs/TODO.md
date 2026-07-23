# TODO — interrupt recovery

Read this after any interruption, then `ROADMAP.md` and `CHANGELOG.md`.

## Now (Phase 0)

- [x] Docs + license + gitignore
- [x] Root config contract
- [x] API domain models + Alembic first migration
- [x] Web dashboard pages wired to API health/settings
- [x] Docker Compose + CI workflow
- [x] API tests (5) + ruff clean; web typecheck
- [ ] Initial git commit (await operator request)
- [ ] Optional: `docker compose up -d postgres redis` + `make migrate` smoke on machine

## Next (Phase 1 kickoff)

- [ ] Experiment CRUD API
- [ ] DataProvider protocol + fake/fixture provider for tests
- [ ] First configurable NSE historical adapter
- [ ] Datasets page showing freshness

## Parking lot

- Desktop packaging
- Options microstructure
- Marketplace payments (keep OSS-first; optional later)
- Vector DB (optional embeddings for literature/search)

## Blockers

- None (greenfield)

## Notes for agents

- Branding is placeholder — use `config.app.name`
- Never hardcode provider URLs or API keys
- Prefer evidence, tests, and reproducibility in every PR
