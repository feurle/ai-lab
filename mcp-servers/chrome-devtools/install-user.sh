#!/usr/bin/env bash
# Installs chrome-devtools-mcp for the CURRENT USER ONLY (no sudo, nothing
# under /usr/local) and registers it with Claude Code, GitHub Copilot CLI and
# opencode.
#
# Claude Code and Copilot CLI are configured through their own `mcp add`
# commands rather than by editing their JSON directly -- both files are managed
# by the tools themselves (~/.claude.json holds far more than MCP config).
# opencode's `mcp add` is interactive, so its config file is edited instead.
set -euo pipefail

npm_prefix="$HOME/.local"
bin_path="$npm_prefix/bin/chrome-devtools-mcp"
opencode_dir="$HOME/.config/opencode"

echo "Installing chrome-devtools-mcp into $npm_prefix (user-only, no sudo) ..."
npm install --prefix "$npm_prefix" --global chrome-devtools-mcp@latest

if [ ! -x "$bin_path" ]; then
  echo "Expected binary not found at $bin_path" >&2
  exit 1
fi

# --- Claude Code (user scope -> ~/.claude.json) ---------------------------
if command -v claude >/dev/null 2>&1; then
  echo "Registering with Claude Code (user scope) ..."
  claude mcp remove -s user chrome-devtools >/dev/null 2>&1 || true
  claude mcp add -s user chrome-devtools -- "$bin_path"
else
  echo "Skipping Claude Code: 'claude' not on PATH"
fi

# --- GitHub Copilot CLI (user config -> ~/.copilot/mcp-config.json) -------
if command -v copilot >/dev/null 2>&1; then
  echo "Registering with GitHub Copilot CLI ..."
  copilot mcp remove chrome-devtools >/dev/null 2>&1 || true
  copilot mcp add chrome-devtools -- "$bin_path"
else
  echo "Skipping Copilot CLI: 'copilot' not on PATH"
fi

# --- opencode (global config; `opencode mcp add` is interactive) ----------
opencode_cfg="$opencode_dir/opencode.jsonc"
if [ -f "$opencode_dir/opencode.json" ] && [ ! -f "$opencode_cfg" ]; then
  opencode_cfg="$opencode_dir/opencode.json"
fi
mkdir -p "$opencode_dir"

echo "Registering with opencode ..."
python3 - "$bin_path" "$opencode_cfg" <<'PY'
import json
import sys
from pathlib import Path

bin_path, cfg = (Path(p) for p in sys.argv[1:3])
entry = {"type": "local", "command": [str(bin_path)], "enabled": True}

data = {"$schema": "https://opencode.ai/config.json", "mcp": {}}
if cfg.exists():
    text = cfg.read_text(encoding="utf-8").strip()
    if text:
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # Real JSONC with comments: cannot be rewritten safely.
            print(f"!! {cfg} could not be parsed and was left unchanged.")
            print('   Add this manually under "mcp":')
            print(json.dumps({"chrome-devtools": entry}, indent=2))
            sys.exit(0)

data.setdefault("mcp", {})["chrome-devtools"] = entry
cfg.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
print(f"Wrote {cfg}")
PY

echo
echo "Done. Verify with: $bin_path --version"
case ":$PATH:" in
  *":$npm_prefix/bin:"*) ;;
  *) echo "Note: $npm_prefix/bin is not on your PATH (configs use the absolute path, so MCP still works)." ;;
esac
