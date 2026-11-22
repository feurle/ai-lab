#!/usr/bin/env bash
# Removes the /send-last symlinks created by install-user.sh. Only symlinks that
# point into this repo are removed; smtp.conf (holds your credentials) is kept.
set -euo pipefail

src_dir="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
config_home="${XDG_CONFIG_HOME:-$HOME/.config}"

unlink_ours() {
  local src="$1" dst="$2"
  if [ -L "$dst" ] && [ "$(readlink -f "$dst")" = "$(readlink -f "$src")" ]; then
    rm "$dst"
    echo "  removed $dst"
  elif [ -e "$dst" ] || [ -L "$dst" ]; then
    echo "  SKIP $dst: not a symlink to this repo" >&2
  else
    echo "  not installed: $dst"
  fi
}

unlink_ours "$src_dir/send-last" "$HOME/.local/bin/send-last"
unlink_ours "$src_dir/send-last.md" "$config_home/opencode/commands/send-last.md"

echo
echo "Kept $config_home/send-last/smtp.conf (contains credentials). Delete it manually if no longer needed."
