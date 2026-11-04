# Installing Panda Federation Tools (for AI coding agents such as Cline)

Follow these steps to add this MCP server for the user.

1. **Check for uv.** Run `uvx --version`. If it is missing, install uv:
   - macOS / Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
2. **Check that the server starts:**
   `uvx --from git+https://github.com/pandadad0214/panda-federation-tools@v1.2.0 panda-federation-tools --version`
   It should print the version number. Each start checks the tagged release on GitHub, so starting can take 15 to 30 seconds.
3. **Ask the user for their Apify API token.** They can copy it from https://console.apify.com/settings/integrations (a free Apify account works). Never print the token back, log it, or commit it.
4. **Add the server** to the MCP settings file (for Cline: `cline_mcp_settings.json`):

```json
{
  "mcpServers": {
    "panda-federation-tools": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/pandadad0214/panda-federation-tools@v1.2.0", "panda-federation-tools"],
      "env": { "APIFY_TOKEN": "<the user's Apify token>" },
      "timeout": 60,
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

   Keep `"timeout": 60`: Cline's default MCP timeout is 10 seconds, which is shorter than the 15 to 30 seconds uvx can take to start the server from GitHub. Without it, Cline reports an `initialize` timeout.
5. **Verify:** the server should list 18 tools (for example `reference_checker`, `literature_search`, `company_hiring_signals`). A cheap first test is `email_domain_security_checker` with `{"domains": ["example.com"], "run_max_items": 1}`.

Optional environment variables: `PANDA_MAX_CHARGE_USD` (default spending cap per call, 0.50), `PANDA_MAX_ITEMS` (default 50), `PANDA_TIMEOUT_SECS` (default 120, max 300).

Each tool call runs on the user's own Apify account and costs a fraction of a cent per result, capped by `run_max_charge_usd`.
