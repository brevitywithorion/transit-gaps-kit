# Security audit

A code-level pre-push audit was run before the private GitHub repository was created.
Full artifacts live **outside** this repo (operator machine path `security-audit/transit-gaps-kit/`).

**Verdict:** PASS for private use. No confirmed vulnerabilities. Residual notes:

- Treat `gtfs.url` as trusted (local operator tool).
- Keep `CENSUS_API_KEY` in the environment only.
- Do not reintroduce Lawrence site Cloudflare functions/secrets into this kit without a fresh audit.
- Outside-in header checks apply only when someone deploys a site built from the kit.

See also [SECURITY.md](../SECURITY.md) and [THIRD_PARTY.md](THIRD_PARTY.md).
