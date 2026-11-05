# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.3.0] - 2026-11-04

### Added
- 5 new MCP tools, now public on the Apify Store: `website_change_monitor`, `sbir_sttr_topic_radar`, `sec_financials_excel`, `clinical_trial_leads` and the free `hidden_ai_instructions_scanner` (23 tools in total).
- `run_max_items` also caps results on `sbir_sttr_topic_radar`, `clinical_trial_leads` and `hidden_ai_instructions_scanner`.

### Changed
- README, `llms.txt` and `llms-full.txt` move these 5 out of "Publishing soon"; Nonprofit Leads, Federal Register Monitor, Product Recall Monitor and VIN Decoder + Recalls are still publishing soon.

## [1.2.0] - 2026-11-04

### Added
- Claude Desktop extension (`.mcpb`) attached to every Release: double-click to install, with a secure token prompt.
- One-click "Add to Cursor" button, and `install.sh` / `install.ps1` helpers.
- Release workflow: on a version tag CI tests, builds the wheel, sdist and `.mcpb`, writes `SHA256SUMS.txt` and creates the GitHub Release. PyPI publishing via Trusted Publishing (no stored token).

### Changed
- README now leads with Install / Use; developer docs moved to "For developers".

## [1.1.1] - 2026-11-03

### Fixed
- `run_max_items` now also sets each Actor's own result limit (for example `maxResults`, `maxDomains`, `maxReferences`) when you leave it unset, so a small `run_max_items` means a small bill and not just a shorter reply. Apify's `maxItems` is not enforced for pay-per-event Actors, which is how these tools are priced. The returned dataset is also limited to `run_max_items`.
- Docs and server instructions now name the per-row summary field correctly (`summary` on the research tools, `agentSummary` on the lead, audit and monitoring tools).

## [1.1.0] - 2026-11-03

### Added
- MCP progress notifications every few seconds while an Actor runs, so clients with request timeouts keep waiting on long runs.
- `Dockerfile` (non-root, stdio) with a CI job that builds and smoke-tests it, and `glama.json` for the Glama MCP directory.
- `py.typed` marker, fuller PyPI classifiers and keywords, Documentation and Source URLs.
- Issue templates, a pull request template, and Dependabot for the Docker base image.
- 16 more tests (46 total): retry safety, connection failures, non-JSON replies, progress, output trimming, run-option defaults, bad environment values, `--version`, and checks that README and `llms-full.txt` prices and install tags match the live catalog.

### Changed
- Retries are now limited to cases where Apify never started a run (HTTP 429 or a failed connection). 5xx replies and dropped connections are no longer retried, so a retry can never start a second, double-charged run.
- Large results are trimmed to whole items so the text sent to the model is always valid JSON (with a `truncated` note); every item stays in `structuredContent`.
- Clearer timeout message (runs that hit `run_timeout_secs` are stopped; partial results stay in the run's dataset).
- Invalid `PANDA_*` environment values now fall back to the defaults with a warning instead of stopping the server.

### Fixed
- `llms-full.txt` now lists all three PDF Table Extractor prices; Apify security contact link in `SECURITY.md`.

## [1.0.0] - 2026-11-03

### Added
- Open-source MCP server (`panda-federation-tools`, Python, stdio) exposing 18 public Panda Federation Apify Actors as tools, with input schemas generated from each Actor's published input schema.
- Strict input validation, per-call spending cap, item cap and timeout, one retry on transient Apify errors, and token redaction in every error.
- `scripts/build_catalog.py` to regenerate the tool catalog from the Apify Store.
- Offline test suite, GitHub Actions CI (ruff, mypy, pytest on Python 3.11–3.13, pip-audit, package build), CodeQL and Dependabot.
- `SECURITY.md`, `CONTRIBUTING.md`, this changelog, client setup for Claude Desktop, Claude Code, Cursor and VS Code, and an M8ven trust badge.

### Earlier
- Tool index (`README.md`, `llms.txt`, `llms-full.txt`), MIT license and `server.json` for the hosted Academic Research MCP Server (`io.github.pandadad0214/panda-research-mcp`, version 1.0.0) in the official MCP Registry.

[Unreleased]: https://github.com/pandadad0214/panda-federation-tools/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/pandadad0214/panda-federation-tools/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/pandadad0214/panda-federation-tools/compare/v1.1.1...v1.2.0
[1.1.1]: https://github.com/pandadad0214/panda-federation-tools/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/pandadad0214/panda-federation-tools/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/pandadad0214/panda-federation-tools/releases/tag/v1.0.0
