#!/usr/bin/env bash
# Installs skills/*/SKILL.md from this repo as symlinks into global,
# per-user skill directories so any project's Claude Code / opencode /
# GitHub Copilot CLI session picks them up.
set -euo pipefail

repo_root="$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)"
skills_dir="$repo_root/skills"

mapfile -t skills < <(
  for f in "$skills_dir"/*/SKILL.md; do
    [ -e "$f" ] || continue
    basename "$(dirname "$f")"
  done
)

if [ "${#skills[@]}" -eq 0 ]; then
  echo "No skills found under $skills_dir" >&2
  exit 1
fi

echo "Skills to install: ${skills[*]}"
echo
echo "Where should these be installed?"
echo "  1) Claude Code (~/.claude/skills/)"
echo "  2) opencode / GitHub Copilot CLI (~/.agents/skills/)"
echo "  3) Both"
read -r -p "Choice [1-3]: " choice

targets=()
case "$choice" in
  1) targets=("$HOME/.claude/skills") ;;
  2) targets=("$HOME/.agents/skills") ;;
  3) targets=("$HOME/.claude/skills" "$HOME/.agents/skills") ;;
  *) echo "Invalid choice: $choice" >&2; exit 1 ;;
esac

for target in "${targets[@]}"; do
  echo
  echo "== $target =="
  mkdir -p "$target"

  installed=0
  already=0
  skipped=0

  for name in "${skills[@]}"; do
    src="$skills_dir/$name"
    link="$target/$name"

    if [ -L "$link" ]; then
      if [ "$(readlink -f "$link")" = "$(readlink -f "$src")" ]; then
        already=$((already + 1))
        continue
      else
        echo "  SKIP $name: existing symlink points elsewhere ($(readlink "$link"))"
        skipped=$((skipped + 1))
        continue
      fi
    elif [ -e "$link" ]; then
      echo "  SKIP $name: $link already exists and is not a symlink"
      skipped=$((skipped + 1))
      continue
    fi

    ln -s "$src" "$link"
    echo "  OK   $name -> $src"
    installed=$((installed + 1))
  done

  echo "  --"
  echo "  installed: $installed, already installed: $already, skipped (conflict): $skipped"
done
