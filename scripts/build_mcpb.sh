#!/usr/bin/env bash
# Builds dist/panda-federation-tools-<version>.mcpb (Claude Desktop extension).
set -euo pipefail
cd "$(dirname "$0")/.."
ver=$(python3 -c 'import tomllib;print(tomllib.load(open("pyproject.toml","rb"))["project"]["version"])')
stage=$(mktemp -d)
cp mcpb/manifest.json mcpb/icon.png pyproject.toml uv.lock README.md LICENSE "$stage/"
cp -r src "$stage/src"
find "$stage" -name __pycache__ -prune -exec rm -rf {} +
sed -i.bak "s/\"version\": \"[^\"]*\"/\"version\": \"$ver\"/" "$stage/manifest.json" && rm "$stage/manifest.json.bak"
mkdir -p dist
npx -y @anthropic-ai/mcpb@latest validate "$stage/manifest.json"
npx -y @anthropic-ai/mcpb@latest pack "$stage" "dist/panda-federation-tools-$ver.mcpb"
rm -rf "$stage"
