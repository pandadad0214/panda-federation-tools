#!/usr/bin/env sh
# Panda Federation Tools installer (macOS/Linux). Installs uv if needed, checks the server starts,
# and prints the config for your MCP client. It never asks for or stores your Apify token.
set -eu
VERSION="${PFT_VERSION:-v1.2.0}"
SRC="git+https://github.com/pandadad0214/panda-federation-tools@${VERSION}"
if ! command -v uvx >/dev/null 2>&1; then
  echo "Installing uv (https://docs.astral.sh/uv/)..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  PATH="$HOME/.local/bin:$PATH"; export PATH
fi
echo "Checking the server starts..."
uvx --from "$SRC" panda-federation-tools --version
if command -v claude >/dev/null 2>&1; then
  echo
  echo "Claude Code detected. Add the server with:"
  echo "  claude mcp add panda-federation-tools --env APIFY_TOKEN=apify_api_YOUR_TOKEN -- uvx --from $SRC panda-federation-tools"
fi
cat <<JSON

Add this to your MCP client config (Cursor: ~/.cursor/mcp.json, Claude Desktop: claude_desktop_config.json):
{
  "mcpServers": {
    "panda-federation-tools": {
      "command": "uvx",
      "args": ["--from", "$SRC", "panda-federation-tools"],
      "env": { "APIFY_TOKEN": "apify_api_YOUR_TOKEN" }
    }
  }
}
Get your token at https://console.apify.com/settings/integrations
JSON
