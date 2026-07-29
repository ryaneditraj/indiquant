# Changelog

## [0.5.0] — 2026-07-28

### Added

- **Google Trends Intelligence Module** (Phase 1 + Phase 2 + modeling)
  - Configurable brand / transactional / category / competitor / risk query universe
  - Entities: DMart, Trent, Reliance Smart, JioMart, BigBasket, Blinkit, Zepto, Nykaa, Titan
  - Fixture collector + optional `pytrends` live pulls with repeat averaging
  - Weekly automation via Celery Beat (`quant_os.trends_collect_all`) + `make trends-collect-all` / cron script
  - Point-in-time raw parquet store + Search Demand Score (QoQ/YoY/festival/cross-signal features)
  - Cross-signal fixture adapters (satellite, app rank, pricing/promo, hiring)
  - Gradient-boosting models (rev / SSS / beat-miss / nowcast / ranking) with conformal bands → `artifacts/trends/`
  - Pre-earnings panel, alerts, PIT backtest, JSON export, multi-entity `/trends` UI
  - Explicit relative-index caveats (never absolute volume); proxy labels until fundamentals wired

### Changed

- OSS packaging polish: README Trends callout + CI badge + OG preview, topics/homepage ready for `ryaneditraj/indiquant`

## [0.4.2] — 2026-07-25

### Changed

- Product rename **Sonar → Indiquant** for GitHub discoverability (avoids SonarQube collision)
- GitHub target: personal account `ryaneditraj/indiquant`
- Star-oriented README, topics list, OG asset refresh

## [0.4.1] — 2026-07-25

### Changed

- UI polish: shared buttons, honest validation/optimization copy, structured Settings
- Action results show accept/reject summaries instead of raw JSON dumps
- Header status reflects API idle / scanning / offline
- Removed dead PlaceholderPage; cleaned Quant OS leftovers

## [0.4.0] — 2026-07-25

### Added

- Product identity: **Indiquant** under **Money Radar** (`moneyradar.in`) by **Thugir Group**
- PolyForm Noncommercial 1.0.0 license (no commercial use without separate license)
- Radar-screen visual system, OG image, JSON-LD, sitemap, robots
- Parent-brand lockups across UI, README, and public settings

### Changed

- Replaces prior product names; repo/app product is Indiquant
- SEO metadata tuned for Indian market quant research discoverability

## [0.3.0] — 2026-07-25

- Interim Pramana branding pass

## [0.2.0] — 2026-07-24

- Forever loop, DuckDB, notebook, charts

## [0.1.0] — 2026-07-24

- Research OS MVP

## [Unreleased]

- N/A
