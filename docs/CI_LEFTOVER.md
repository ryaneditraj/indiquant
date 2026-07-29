# CI workflow leftover

**Status (tick 1):** `.github/workflows/ci.yml` exists locally (API ruff+pytest, web typecheck) but is **not** on `origin/main`. Soft-parked on `backup/local-ci` so product commits can push without `workflow` scope.

## Why

Pushing or updating GitHub Actions workflow files requires a GitHub token with the **`workflow`** scope. Current `gh` auth has `gist`, `read:org`, `repo` only. Device-flow refreshes for `workflow` were started earlier and timed out (user asleep).

## Local artifact

- Path: `.github/workflows/ci.yml` (keep **untracked** until scope is available)
- Prior local CI tip: branch `backup/local-ci`

## Unblock

```bash
gh auth refresh -h github.com -s repo,workflow,read:org
git checkout backup/local-ci -- .github/workflows/ci.yml
git add .github/workflows/ci.yml
git commit -m "Add GitHub Actions CI for API tests and web typecheck."
git push origin main
```

Then restore the live CI badge in README (replace the honest “tests local” badge).

Until then: `make api-test` and `cd apps/web && npm run typecheck`.
