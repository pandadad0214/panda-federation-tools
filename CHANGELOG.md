# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.0.0] - 2026-11-03

### Added
- Open-source MCP server (`panda-federation-tools`, Python, stdio) exposing 18 public Panda Federation Apify Actors as tools, with input schemas generated from each Actor's published input schema.
- Strict input validation, per-call spending cap, item cap and timeout, one retry on transient Apify errors, and token redaction in every error.
- `scripts/build_catalog.py` to regenerate the tool catalog from the Apify Store.
- Offline test suite, GitHub Actions CI (ruff, mypy, pytest on Python 3.11–3.13, pip-audit, package build), CodeQL and Dependabot.
- `SECURITY.md`, `CONTRIBUTING.md`, this changelog, client setup for Claude Desktop, Claude Code, Cursor and VS Code, and an M8ven trust badge.

### Earlier
- Tool index (`README.md`, `llms.txt`, `llms-full.txt`), MIT license and `server.json` for the hosted Academic Research MCP Server (`io.github.pandadad0214/panda-research-mcp`, version 1.0.0) in the official MCP Registry.

[Unreleased]: https://github.com/pandadad0214/panda-federation-tools/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/pandadad0214/panda-federation-tools/releases/tag/v1.0.0
