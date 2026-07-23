# Changelog

All notable changes to this project are documented here.

Format inspired by [Keep a Changelog](https://keepachangelog.com/).
Versioning follows [SemVer](https://semver.org/) once we tag `0.1.0`.

## [Unreleased]

### Added

- Repository foundation: README, LICENSE (MIT), CONTRIBUTING, ROADMAP, architecture docs
- Root configuration contract: `.env.example`, `config.yaml`
- `apps/api` FastAPI skeleton with health/settings endpoints and domain model stubs
- `apps/web` Next.js dashboard shell (dark professional research OS layout)
- Docker Compose for PostgreSQL and Redis
- GitHub Actions CI smoke (API lint/tests, web typecheck)
- `docs/TODO.md` for interrupt-safe recovery

### Changed

- N/A (initial)

### Security

- Secrets excluded via `.gitignore`; documented never-commit policy
