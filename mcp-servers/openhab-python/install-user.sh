#!/usr/bin/env bash
# Registers the openhab-python MCP server for the CURRENT USER ONLY with Claude
# Code, GitHub Copilot CLI and opencode, so it is available outside this repo.
#
# The server runs from this checkout via `uv --directory <this dir> run ...`.
# Moving the repo means re-running this script.
#
# Secrets (OPENHAB_API_TOKEN, OPENHAB_BASE_URL) live in one user-owned file,
# ${XDG_CONFIG_HOME:-~/.config}/openhab-mcp/.env (mode 0600), which the server
# loads itself. They are deliberately NOT passed via `mcp add -e/--env`: that
# would put plaintext copies of the token into three tool-managed configs.
# Precedence: environment > project .env > user file.
#
# Claude Code and Copilot CLI are configured through their own `mcp add`
# commands rather than by editing their JSON directly -- both files are managed
# by the tools themselves (~/.claude.json holds far more than MCP config).
# opencode's `mcp add` is interactive, so its config file is edited instead.
set -euo pipefail

name="mcp-openhab-python"
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
opencode_dir="$HOME/.config/opencode"
user_env="${XDG_CONFIG_HOME:-$HOME/.config}/openhab-mcp/.env"

# Absolute path: MCP clients may not have ~/.local/bin on their PATH.
uv_bin="$(command -v uv || true)"
if [ -z "$uv_bin" ] && [ -x "$HOME/.local/bin/uv" ]; then
  uv_bin="$HOME/.local/bin/uv"
fi
if [ -z "$uv_bin" ]; then
  echo "uv not found. Install it: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
  exit 1
fi

cmd=("$uv_bin" --directory "$project_dir" run openhab-mcp --transport stdio)

echo "Syncing dependencies in $project_dir ..."
"$uv_bin" --directory "$project_dir" sync

# --- User secrets file ------------------------------------------------------
write_user_env() {  # $1 = base url, $2 = token
  (
    umask 077
    mkdir -p "$(dirname "$user_env")"
    printf 'OPENHAB_BASE_URL=%s\nOPENHAB_API_TOKEN=%s\n' "$1" "$2" >"$user_env"
  )
  chmod 600 "$user_env"
  echo "Wrote $user_env (mode 600)"
}

if [ -f "$user_env" ]; then
  echo "Using existing secrets file $user_env (left unchanged)"
elif [ -t 0 ]; then
  seeded=false
  if grep -qE '^[[:space:]]*OPENHAB_API_TOKEN=.+' "$project_dir/.env" 2>/dev/null; then
    read -rp "Copy OPENHAB_* settings from $project_dir/.env to $user_env? [Y/n] " answer
    if [[ ! "$answer" =~ ^[Nn] ]]; then
      (umask 077 && mkdir -p "$(dirname "$user_env")" &&
        grep -E '^[[:space:]]*OPENHAB_' "$project_dir/.env" >"$user_env")
      chmod 600 "$user_env"
      echo "Wrote $user_env (mode 600)"
      seeded=true
    fi
  fi
  if [ "$seeded" = false ]; then
    read -rp "OpenHAB base URL [http://localhost:8080]: " base_url
    read -rsp "OpenHAB API token (input hidden, empty to skip): " token
    echo
    if [ -n "$token" ]; then
      write_user_env "${base_url:-http://localhost:8080}" "$token"
    else
      echo "!! No token given; create $user_env later (see .env.example)."
    fi
  fi
else
  echo "!! $user_env not found and no terminal to prompt on. Create it (mode 600) with"
  echo "   OPENHAB_API_TOKEN and OPENHAB_BASE_URL (see .env.example), or the server will fail to start."
fi

# --- Claude Code (user scope -> ~/.claude.json) ---------------------------
if command -v claude >/dev/null 2>&1; then
  echo "Registering with Claude Code (user scope) ..."
  claude mcp remove -s user "$name" >/dev/null 2>&1 || true
  claude mcp add -s user "$name" -- "${cmd[@]}"
else
  echo "Skipping Claude Code: 'claude' not on PATH"
fi

# --- GitHub Copilot CLI (user config -> ~/.copilot/mcp-config.json) -------
if command -v copilot >/dev/null 2>&1; then
  echo "Registering with GitHub Copilot CLI ..."
  copilot mcp remove "$name" >/dev/null 2>&1 || true
  copilot mcp add "$name" -- "${cmd[@]}"
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
python3 - "$name" "$opencode_cfg" "${cmd[@]}" <<'PY'
import json
import sys
from pathlib import Path

name, cfg, command = sys.argv[1], Path(sys.argv[2]), sys.argv[3:]
entry = {"type": "local", "command": command, "enabled": True}

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
            print(json.dumps({name: entry}, indent=2))
            sys.exit(0)

data.setdefault("mcp", {})[name] = entry
cfg.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
print(f"Wrote {cfg}")
PY

echo
echo "Done. Verify with: claude mcp get $name"
echo "Note: the registration points at $project_dir -- re-run this script if you move the repo."
