# Contributing

Thanks for helping improve Panda Federation Tools. Issues, bug reports and pull requests are welcome.

## Ground rules
- Be kind and specific. Describe the problem, what you expected, and how to reproduce it.
- Never paste an API token into an issue, PR, test or log. Tests must not need a token or network access.
- Security problems go through [SECURITY.md](SECURITY.md), not public issues.

## Set up

```bash
git clone https://github.com/pandadad0214/panda-federation-tools && cd panda-federation-tools
uv sync            # Python 3.11+; installs the pinned versions from uv.lock
```

## Before you open a pull request

```bash
uv run ruff format .
uv run ruff check .
uv run mypy
uv run pytest
```

CI runs the same checks on Python 3.11, 3.12 and 3.13, plus `pip-audit` and CodeQL. Keep pull requests small and focused, and add a line to [CHANGELOG.md](CHANGELOG.md) under "Unreleased".

## Adding or updating a tool
Tools are generated from the public Apify Store, so the MCP schema always matches the Actor.

1. Add the Actor slug to `SLUGS` in `scripts/build_catalog.py` (the Actor must be public).
2. Run `python scripts/build_catalog.py` to refresh `src/panda_federation_tools/catalog.json`.
3. Add the tool to the table in `README.md` and to `llms.txt` and `llms-full.txt`. `tests/test_catalog.py` fails if any of them is missing.
4. Run the checks above and open a pull request.

## Dependencies
Pin new dependencies exactly in `pyproject.toml`, run `uv lock`, and commit `uv.lock`. Dependabot proposes updates weekly.

## Releases
Bump the version in `pyproject.toml`, `src/panda_federation_tools/__init__.py` and `server.json` together (a test checks they match), update the changelog, then tag `vX.Y.Z`.
