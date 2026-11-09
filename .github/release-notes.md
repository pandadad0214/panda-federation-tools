**Prefer a focused domain server** (TDQS). From [PyPI](https://pypi.org/project/panda-federation-tools/) (needs [uv](https://docs.astral.sh/uv/) and a free [Apify token](https://console.apify.com/settings/integrations)):

```bash
uvx --from panda-federation-tools@{{VERSION}} panda-research-tools
uvx --from panda-federation-tools@{{VERSION}} panda-public-funding-tools
uvx --from panda-federation-tools@{{VERSION}} panda-leads-tools
uvx --from panda-federation-tools@{{VERSION}} panda-web-security-tools
```

Compatibility mega-server (all tools): `uvx panda-federation-tools@{{VERSION}}`

- **Claude Desktop:** download `panda-federation-tools-{{VERSION}}.mcpb` below and double-click it (umbrella).
- **Cursor:** see domain examples in the [README](https://github.com/pandadad0214/panda-federation-tools#install-for-your-client-focused-servers).
- **Helper scripts:** `install.sh` (macOS/Linux) or `install.ps1` (Windows). Verify with `SHA256SUMS.txt`.

### Added
- 4 new tools, now public on the Apify Store (36 in total): `new_york_new_business_leads`, `h1b_lca_sponsor_leads`, `eu_ted_tenders` (leads, 15 tools) and `broken_link_checker` (web-security, 6 tools).
- TDQS-grade descriptions for each new tool (nearest sibling, when / when not, billing and parameter interactions, return shape).

### Changed
- Domain server instructions, README, `llms.txt` and `llms-full.txt` list the new tools; nothing is queued as publishing soon.

Full history: [CHANGELOG.md](https://github.com/pandadad0214/panda-federation-tools/blob/main/CHANGELOG.md).
