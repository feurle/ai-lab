#!/usr/bin/env bash
# Installs the /send-last opencode command for the CURRENT USER ONLY (no sudo).
#
#   ~/.local/bin/send-last                       -> commands/send-last/send-last
#   ~/.config/opencode/commands/send-last.md     -> commands/send-last/send-last.md
#   ${XDG_CONFIG_HOME:-~/.config}/send-last/smtp.conf  (created from the example, 0600)
#
# Symlinks are used so edits in the repo apply immediately. Existing files that
# are not symlinks to this repo are never overwritten.
set -euo pipefail

src_dir="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
config_home="${XDG_CONFIG_HOME:-$HOME/.config}"
bin_link="$HOME/.local/bin/send-last"
cmd_link="$config_home/opencode/commands/send-last.md"
smtp_dir="$config_home/send-last"
smtp_conf="$smtp_dir/smtp.conf"

if ! command -v uv >/dev/null 2>&1 && [ ! -x "$HOME/.local/bin/uv" ]; then
  echo "'uv' not found: send-last runs through 'uv run --script' to get its 'markdown' dependency." >&2
  echo "Install it first: https://docs.astral.sh/uv/" >&2
  exit 1
fi

link() {
  local src="$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  if [ -L "$dst" ]; then
    if [ "$(readlink -f "$dst")" = "$(readlink -f "$src")" ]; then
      echo "  already installed: $dst"
      return 0
    fi
    echo "  SKIP $dst: existing symlink points elsewhere ($(readlink "$dst"))" >&2
    return 1
  elif [ -e "$dst" ]; then
    echo "  SKIP $dst: already exists and is not a symlink (remove it and re-run)" >&2
    return 1
  fi
  ln -s "$src" "$dst"
  echo "  OK   $dst -> $src"
}

status=0
echo "Linking send-last ..."
link "$src_dir/send-last" "$bin_link" || status=1
link "$src_dir/send-last.md" "$cmd_link" || status=1

if [ -e "$smtp_conf" ]; then
  echo "SMTP config exists: $smtp_conf"
else
  mkdir -p "$smtp_dir"
  install -m 600 "$src_dir/smtp.conf.example" "$smtp_conf"
  echo "Created $smtp_conf (mode 600) from the example -- edit user/password/from."
fi

case ":$PATH:" in
  *":$HOME/.local/bin:"*) ;;
  *) echo "Note: $HOME/.local/bin is not on your PATH (the command uses the absolute path, so it still works)." ;;
esac

echo
echo "Done. Try it inside opencode: /send-last you@example.com"
exit "$status"
