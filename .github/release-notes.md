**Install in one command** (needs [uv](https://docs.astral.sh/uv/) and a free [Apify token](https://console.apify.com/settings/integrations)):

```bash
uvx --from git+https://github.com/pandadad0214/panda-federation-tools@v1.2.0 panda-federation-tools
```

- **Claude Desktop:** download `panda-federation-tools-1.2.0.mcpb` below and double-click it.
- **Cursor:** use the "Add to Cursor" button in the [README](https://github.com/pandadad0214/panda-federation-tools#install--use).
- **Helper scripts:** `install.sh` (macOS/Linux) or `install.ps1` (Windows). One package works on every OS.
- Verify downloads with `SHA256SUMS.txt`.

### Added
- Claude Desktop extension (.mcpb) with a secure token prompt.
- One-click Cursor install button; install.sh / install.ps1 helpers.
- Release assets built and checksummed automatically by CI; PyPI publishing via Trusted Publishing.

### Changed
- README now leads with Install / Use; developer docs moved to "For developers".

18 tools, same prices. Your `APIFY_TOKEN` only goes to api.apify.com. Full history: [CHANGELOG.md](https://github.com/pandadad0214/panda-federation-tools/blob/main/CHANGELOG.md).
