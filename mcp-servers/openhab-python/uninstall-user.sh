#!/usr/bin/env bash
# Removes the per-user openhab-python MCP registrations (Claude Code, Copilot
# CLI, opencode) written by install-user.sh. The checkout and its .venv are
# left untouched; the project-scoped .mcp.json / opencode.jsonc still work.
# The user secrets file is kept too -- delete it yourself if the token should go.
set -euo pipefail

name="mcp-openhab-python"
opencode_dir="$HOME/.config/opencode"
user_env="${XDG_CONFIG_HOME:-$HOME/.config}/openhab-mcp/.env"

if command -v claude >/dev/null 2>&1; then
  echo "Removing from Claude Code (user scope) ..."
  claude mcp remove -s user "$name" || true
else
  echo "Skipping Claude Code: 'claude' not on PATH"
fi

if command -v copilot >/dev/null 2>&1; then
  echo "Removing from GitHub Copilot CLI ..."
  copilot mcp remove "$name" || true
else
  echo "Skipping Copilot CLI: 'copilot' not on PATH"
fi

python3 - "$name" "$opencode_dir/opencode.jsonc" "$opencode_dir/opencode.json" <<'PY'
import json
import sys
from pathlib import Path

name = sys.argv[1]

for path in (Path(p) for p in sys.argv[2:]):
    if not path.exists():
        print(f"Skipping: {path} not found")
        continue
    try:
        data = json.loads(path.read_text(encoding="utf-8") or "{}")
    except json.JSONDecodeError:
        print(f"!! Could not parse {path}; remove the {name} entry manually")
        continue
    section = data.get("mcp")
    if isinstance(section, dict) and name in section:
        del section[name]
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"Updated {path}")
    else:
        print(f"No {name} entry in {path}")
PY

if [ -f "$user_env" ]; then
  echo "Kept secrets file $user_env -- remove it with: rm \"$user_env\""
fi

echo "Done."
