# Overnight Indiquant sprint log

Continuous OSS + product grind while the user sleeps (~5h window). Push when safe; no force; no secrets; no fake return claims.

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

- _(pending)_ — Trends hardening + OSS demo polish + overnight sprint docs

### Next ideas (later ticks)

1. Push CI once `workflow` scope available; restore Actions badge
2. Export CSV for Trends scores; screenshot/GIF notes for README
3. Fundamentals store stub to retire proxy model labels
4. Harden pytrends rate-limit / backoff path
5. Tiny “copy curl” helper on empty `/trends`

---
