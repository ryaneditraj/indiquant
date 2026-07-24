# Contributing to Pramana

Thank you for helping build an evidence-first quant research OS.

## Ground rules

1. **Edge over theater** — Changes should help discover or validate real market edges.
2. **No hardcoding** — External URLs, keys, providers, brokers, models → config.
3. **Reproducibility** — Experiments need IDs, inputs, seeds, and metrics.
4. **Evidence** — Prefer tests and statistical checks over “it looked good.”
5. **No secrets** — Never commit `.env`, keys, or credentials.
6. **Brand** — Product name is **Pramana**; keep tone precise and non-hype. See [docs/brand.md](docs/brand.md).

## Development setup

See [README.md](README.md) quick start.

```bash
make api-test   # backend
cd apps/web && npm run typecheck
```

## Branch & PR workflow

1. Fork / branch from `main`
2. Keep PRs focused (one concern)
3. Update docs + `CHANGELOG.md` Unreleased when user-facing
4. Update `ROADMAP.md` if you complete a roadmap item
5. Ensure CI passes

### PR checklist

- [ ] Tests added/updated
- [ ] Docs updated if behavior/API changed
- [ ] Config documented if new external dependency
- [ ] No secrets or large binary dumps
- [ ] Indian market assumptions documented when NSE/BSE-specific
- [ ] Passes the edge test (above)

## Code style

| Area | Tool |
|------|------|
| Python | Ruff (+ Black/MyPy available) |
| TypeScript | ESLint + TypeScript strict |
| Commits | Imperative, why-focused |

## Architecture expectations

- Prefer plugins/interfaces for data providers, brokers, AI models, validators
- Keep research loop agents thin; heavy logic in testable libraries
- Dashboard is the heart — live, clear, minimal clutter

## Reporting issues

Include OS/arch, redacted config shape, steps, expected vs actual, experiment IDs.

## License

By contributing, you agree your contributions are licensed under the MIT License.
