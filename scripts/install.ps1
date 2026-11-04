# Panda Federation Tools installer (Windows PowerShell). Installs uv if needed, checks the server starts,
# and prints the config for your MCP client. It never asks for or stores your Apify token.
$ErrorActionPreference = "Stop"
$Version = if ($env:PFT_VERSION) { $env:PFT_VERSION } else { "v1.2.0" }
$Src = "git+https://github.com/pandadad0214/panda-federation-tools@$Version"
if (-not (Get-Command uvx -ErrorAction SilentlyContinue)) {
  Write-Host "Installing uv (https://docs.astral.sh/uv/)..."
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
}
Write-Host "Checking the server starts..."
uvx --from $Src panda-federation-tools --version
Write-Host @"

Add this to your MCP client config (Cursor: %USERPROFILE%\.cursor\mcp.json, Claude Desktop: claude_desktop_config.json):
{
  "mcpServers": {
    "panda-federation-tools": {
      "command": "uvx",
      "args": ["--from", "$Src", "panda-federation-tools"],
      "env": { "APIFY_TOKEN": "apify_api_YOUR_TOKEN" }
    }
  }
}
Get your token at https://console.apify.com/settings/integrations
"@
