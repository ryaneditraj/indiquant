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

## Setup

See [README.md](README.md).

```bash
make api-test
cd apps/web && npm run typecheck
```

## PRs

Focused PRs. Update CHANGELOG for user-facing changes. Pass the edge test.

## Code of conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
