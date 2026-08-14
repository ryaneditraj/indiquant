# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.5.x   | ✅ |
| 0.4.x   | security fixes only |

## Reporting

Do **not** open public issues for security bugs.

Contact Thugir Group / Money Radar via [moneyradar.in](https://moneyradar.in) (or GitHub Security Advisories when enabled) with impact, repro, and version.

## Notes

- Never commit `.env` or API keys
- Notebook execute is a restricted research REPL — not a multi-tenant sandbox
- Rotate `SECRET_KEY` before any networked deployment
- `/api/v1/security/encrypt` and `/decrypt` are local helpers; they return 403 when `QUANT_OS_ENV` is production or staging
