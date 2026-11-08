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
- 5 new tools, now public on the Apify Store (32 in total): `building_permit_leads`, `florida_new_business_leads`, `texas_new_business_leads` (leads, 12 tools), `bulk_domain_whois_expiry` (web-security, 5 tools) and `wayback_snapshot_finder` (research, 7 tools).
- TDQS-grade descriptions for each new tool (nearest sibling, when / when not, billing and parameter interactions, return shape).

### Changed
- Domain server instructions, README, `llms.txt` and `llms-full.txt` list the new tools; H-1B LCA Sponsor Leads is still publishing soon.

Full history: [CHANGELOG.md](https://github.com/pandadad0214/panda-federation-tools/blob/main/CHANGELOG.md).
