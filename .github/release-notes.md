**Prefer a focused domain server** (TDQS). From [PyPI](https://pypi.org/project/panda-federation-tools/) (needs [uv](https://docs.astral.sh/uv/) and a free [Apify token](https://console.apify.com/settings/integrations)):

```bash
uvx --from panda-federation-tools@{{VERSION}} panda-research-tools
uvx --from panda-federation-tools@{{VERSION}} panda-public-funding-tools
uvx --from panda-federation-tools@{{VERSION}} panda-leads-tools
uvx --from panda-federation-tools@{{VERSION}} panda-web-security-tools
```

Compatibility mega-server (all tools): `uvx panda-federation-tools@{{VERSION}}`

- **Claude Desktop:** download `panda-federation-tools-{{VERSION}}.mcpb` below and double-click it (umbrella).
- **Cursor:** see domain examples in the [README](https://github.com/pandadad0214/panda-federation-tools#install--use-focused-servers).
- **Helper scripts:** `install.sh` (macOS/Linux) or `install.ps1` (Windows). Verify with `SHA256SUMS.txt`.

### Added
- Focused domain MCP entry points + `PFT_DOMAIN` filter (research / public-funding / leads / web-security).
- TDQS-grade tool descriptions for all 23 tools.

### Changed
- Umbrella README is an index; recommended install path is a domain server, not the 23-tool mega-server.

Full history: [CHANGELOG.md](https://github.com/pandadad0214/panda-federation-tools/blob/main/CHANGELOG.md).
