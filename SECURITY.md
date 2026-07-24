# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.3.x   | ✅ |
| < 0.3   | Best effort |

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security bugs.

Email maintainers privately (or use GitHub Security Advisories when enabled) with:

- Description and impact
- Reproduction steps
- Affected version / commit
- Suggested fix if you have one

We aim to acknowledge within 72 hours.

## Hardening notes

- Never commit `.env` or API keys
- Rotate `SECRET_KEY` / `ENCRYPTION_KEY` before networked deployments
- Notebook execute is intentionally restricted — treat it as research REPL, not multi-tenant sandbox
- Prefer SQLite only for single-user local research
