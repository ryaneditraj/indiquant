# Public-release checklist

**v0.5.x — Indiquant** · Google Trends Intelligence (multi-entity + modeling) is in tree.

## Before making the GitHub repo public

- [x] Public repo `ryaneditraj/indiquant` exists
- [ ] Paste GitHub About + topics (see maintainer notes; `gh repo edit` in release pass)
- [x] `app.github_url` in `config.yaml` is `https://github.com/ryaneditraj/indiquant`
- [x] `.github/workflows/ci.yml` is in the tree (Ruff, pytest, web typecheck)
- [x] UI screenshots captured from the local fixture demo into `docs/screenshots/`
- [ ] Point moneyradar.in/indiquant at the live docs or dashboard when ready
- [x] Do not commit `.env`; rotate any real keys (none should be in git)

## Trends follow-ups (non-blocking)

- [ ] Replace proxy model labels with filings / SSS / beat-miss fundamentals
- [ ] Swap cross-signal fixture adapters for live satellite / app / pricing / hiring feeds
- [ ] Temporal sequence models once multi-year live history exists
