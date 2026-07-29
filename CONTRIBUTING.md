# Contributing to Indiquant

Indiquant is a **Money Radar** product by **Thugir Group**.

## License reminder

This project uses **PolyForm Noncommercial 1.0.0**. Contributions are accepted under the same terms. Commercial use requires a separate license from Thugir Group / Money Radar ([moneyradar.in](https://moneyradar.in)).

## Ground rules

1. **Edge over theater** — Help discover or validate real market edges.
2. **No hardcoding** — Providers, URLs, keys → config.
3. **Reproducibility** — Experiment IDs, inputs, seeds, metrics.
4. **Evidence** — Tests and statistics over vibes.
5. **No secrets** in git.
6. **Brand** — Keep Indiquant ↔ Money Radar ↔ Thugir Group hierarchy clear. See [docs/brand.md](docs/brand.md).
7. **Honest Trends** — Never claim absolute search volume or guaranteed returns.

## Setup

See [README.md](README.md). Trends module overview: [docs/trends.md](docs/trends.md).

```bash
cp .env.example .env
make api-install && make web-install
make demo                 # sample OHLCV + fixture Trends (dmart/trent)
make api-test
cd apps/web && npm run typecheck
```

Useful targets:

| Target | Purpose |
|--------|---------|
| `make demo` | Offline star-path: seed + Trends fixtures |
| `make trends-demo` | Fixture collect/score for dmart + trent |
| `make trends-train` | Proxy GB models (not fundamentals) |
| `make api-test` | Pytest |
| `make smoke` | curl smoke vs `:8000` |

## PRs

Focused PRs. Update CHANGELOG for user-facing changes. Pass the edge test.

- Prefer fixture-backed tests for Google Trends / providers (no live keys in CI).
- Keep PolyForm NC language intact in README and docs.
- Surface Trends caveats on any new scoring / ranking UI.
- Empty-state UX beats silent failures — especially on `/trends`.

## Code of conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
