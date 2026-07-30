# Overnight Indiquant sprint log

Continuous OSS + product grind while the user sleeps (~5h window). Push when safe; no force; no secrets; no fake return claims.

---

## Sync + catch-up — 2026-07-30 ~08:30 IST

### Overnight loop status

- Loop terminal `653025` still alive (~5.7h+); **only Tick 1 echoed** in the shell log (Ticks 2–10 never wrote entries despite schedule)
- Docs had Tick 0 + Tick 1 only → **one catch-up grind** for missed 2–N priorities

### Git sync (no force-push)

- `origin/main` was ahead/divergent: local tip still carried CI commit `0b95cde` while remote had PR merge `f818a5c` (+ later note `151bcd1`)
- Parked CI on `backup/local-ci` → `0b95cde` (branch kept; **not** deleted)
- `git reset --hard origin/main` on local `main`; restored `.github/workflows/ci.yml` as **untracked**
- Local `main` matches `origin/main` at catch-up start (`151bcd1`)

### Catch-up shipped (branch `overnight/catchup-ticks2-n` → PR)

- Comparison ranking **CSV/JSON export** (`GET /trends/comparison?format=csv`) + view-aware Export buttons
- Comparison empty_state / next_steps + export error surfacing + copy-curl on empty ranking
- Celery Beat smoke test + `make trends-beat-smoke`
- Thin `trends/fundamentals.py` stub (`load_labels` → None) + `label_source` in train/predict meta
- Docs/README: comparison CSV + Beat smoke; no fake CI badge
- Verify: **38** pytest passed; `tsc` green
- CI still **auth-blocked** (token scopes: gist, read:org, repo — no `workflow`)

### Tree left for remaining ticks

- On feature branch until PR merges; `main` stays aligned with origin after merge
- `backup/local-ci` intact; `ci.yml` untracked locally
- Loop may still fire late ticks — prefer small additive work, avoid re-diverging CI onto `main`

---

## Tick 1 — export + backoff · 2026-07-30 ~02:35 IST

### Status check

- CI still **auth-blocked** (`workflow` scope missing on `gh` token) — skip workflow push
- `git push origin main` rejected: OAuth App cannot update `.github/workflows/ci.yml`
- Soft-park CI: rebase product commits onto `origin/main`, keep workflow on `backup/local-ci`, leave `ci.yml` untracked locally

### Verification

- `pytest` apps/api: **34 passed**
- `tsc` apps/web: green

### Shipped this tick

- Trends **CSV export** (`?format=csv`) + UI Export CSV button (relative indices only)
- Empty `/trends` **copy collect curl** helper
- **pytrends** exponential backoff + request gaps (`call_with_backoff`, config knobs)
- Edge tests: CSV export, empty export soft-fail, backoff retry/exhaust
- README screenshot/GIF notes for star-magnet demos; docs/trends CSV + live backoff notes
- gitignore Trends run JSON clutter under `data/parquet/trends/**/runs/`

### Commits

- _(this tick)_ — CSV export, pytrends backoff, empty-state curl, docs polish
- Rebase: drop CI workflow commit from `main` tip so non-workflow work can push

### Next ideas (later ticks)

1. Push CI once `workflow` scope available; restore Actions badge
2. Fundamentals store stub to retire proxy model labels
3. Capture / commit `trends-demo.gif` after a real local demo
4. Comparison-view CSV export of rankings
5. Celery Beat docs smoke for weekly Trends

---

## Tick 0 — bootstrap · 2026-07-30 ~02:05 IST

### Status check

- Repo clean on `main`; remote `origin` = `https://github.com/ryaneditraj/indiquant.git`
- Finish-CI agent had committed CI locally (`2bbea20`) but could not push (`workflow` scope missing)
- Soft-parked that commit onto `backup/local-ci`; left `.github/workflows/ci.yml` **untracked** so other work can push
- Auth refresh device flows still waiting — user asleep → documented in [CI_LEFTOVER.md](./CI_LEFTOVER.md)

### Verification

- `pytest` apps/api: **26+ edge tests** (after new Trends cases) — green
- `tsc` apps/web: green

### Shipped this tick

- Trends ranking polish: quality tie-break, `ranking_method`, unreliable → `side_hint=watch`, clearer proxy caveats
- Soft failure paths: empty dashboard `empty_state` + `next_steps`; unknown entities in ranking don’t abort
- Edge-case tests for empty/partial rank, bad provider 400, empty dashboard
- `/trends` empty-state UX (entity + comparison) with `make trends-demo` guidance
- Makefile: `trends-demo`, `demo` (seed + Trends fixtures)
- README: 60s demo path, Makefile quick start, honest “tests local” badge (no fake CI green)
- CONTRIBUTING + docs/trends updates
- CI leftover note (no destructive conflict with finish-CI)

### Commits

- `14ded37` — Trends empty states, ranking caveats, offline demo path, CI leftover docs (on `origin/main`)

### Next ideas (later ticks)

1. Push CI once `workflow` scope available; restore Actions badge
2. Export CSV for Trends scores; screenshot/GIF notes for README
3. Fundamentals store stub to retire proxy model labels
4. Harden pytrends rate-limit / backoff path
5. Tiny “copy curl” helper on empty `/trends`

---
