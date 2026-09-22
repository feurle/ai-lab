#!/usr/bin/env bash
# Removes the per-user chrome-devtools-mcp install and its MCP registrations
# (Claude Code, Copilot CLI, opencode). Also cleans up the legacy ~/.mcp.json
# entry written by earlier versions of the install script -- no tool ever read
# that file.
set -euo pipefail

npm_prefix="$HOME/.local"
opencode_dir="$HOME/.config/opencode"

if command -v claude >/dev/null 2>&1; then
  echo "Removing from Claude Code (user scope) ..."
  claude mcp remove -s user chrome-devtools || true
else
  echo "Skipping Claude Code: 'claude' not on PATH"
fi

if command -v copilot >/dev/null 2>&1; then
  echo "Removing from GitHub Copilot CLI ..."
  copilot mcp remove chrome-devtools || true
else
  echo "Skipping Copilot CLI: 'copilot' not on PATH"
fi

python3 - "$opencode_dir/opencode.jsonc" "$opencode_dir/opencode.json" "$HOME/.mcp.json" <<'PY'
import json
import sys
from pathlib import Path

opencode_jsonc, opencode_json, legacy_mcp_json = (Path(p) for p in sys.argv[1:4])


def edit(path, key):
    if not path.exists():
        print(f"Skipping: {path} not found")
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8") or "{}")
    except json.JSONDecodeError:
        print(f"!! Could not parse {path}; remove the chrome-devtools entry manually")
        return
    section = data.get(key)
    if isinstance(section, dict) and "chrome-devtools" in section:
        del section["chrome-devtools"]
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"Updated {path}")
    else:
        print(f"No chrome-devtools entry in {path}")


edit(opencode_jsonc, "mcp")
edit(opencode_json, "mcp")
edit(legacy_mcp_json, "mcpServers")  # legacy, unread by any tool
PY

echo "Uninstalling chrome-devtools-mcp from $npm_prefix ..."
npm uninstall --prefix "$npm_prefix" --global chrome-devtools-mcp || true

echo "Done."
