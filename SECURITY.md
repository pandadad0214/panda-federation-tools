# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| 1.x (latest `main` and the newest tag) | Yes |
| Older tags | No, please upgrade |

## Reporting a vulnerability

Please report security issues privately, not in a public issue:

[Open a private vulnerability report](https://github.com/pandadad0214/panda-federation-tools/security/advisories/new) on GitHub (Security tab → Report a vulnerability). If that is not possible, open a public issue that says only "security contact requested" and we will reach out privately.

Include what you found, how to reproduce it, and the impact. We acknowledge reports within 2 business days and aim to ship a fix for confirmed high-severity issues within 7 days. We credit reporters in the changelog unless you ask us not to.

## Scope

In scope: the MCP server in `src/`, the catalog generator in `scripts/`, the CI workflows, and the `server.json` registry metadata.

For the hosted Apify Actors themselves (data quality, a bug in a run), open an issue on that Actor's Apify Issues tab. For Apify platform issues, contact [Apify](https://apify.com/security).

## How this server protects you

- **Secrets:** `APIFY_TOKEN` is read from the environment, sent only to `https://api.apify.com` in an `Authorization` header, redacted from all error text, and never logged or returned to the model. The repository contains no secrets; `.env` files are git-ignored.
- **Network:** the server runs locally over stdio, opens no listening ports, and makes outbound requests only to the Apify API.
- **Inputs:** every tool call is validated against a strict JSON Schema (no unknown fields, typed, with ranges) before any run starts. Secret Actor inputs are not exposed as tool parameters.
- **Cost and time limits:** per-call spending cap (`run_max_charge_usd`), item cap and timeout.
- **Tools are read-only:** they fetch public data and do not modify your systems.
- **Supply chain:** pinned dependencies with a committed `uv.lock`, `pip-audit` and CodeQL in CI, Dependabot for Python and GitHub Actions updates, and Actions pinned to commit SHAs with read-only default permissions.

## Use a scoped token

Create a dedicated Apify API token for MCP use and limit it to running Actors where your plan allows [scoped tokens](https://docs.apify.com/platform/integrations/api#api-tokens). Rotate it in the Apify Console if it is ever exposed.
