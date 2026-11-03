# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

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

[Unreleased]: https://github.com/pandadad0214/panda-federation-tools/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/pandadad0214/panda-federation-tools/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/pandadad0214/panda-federation-tools/releases/tag/v1.0.0
