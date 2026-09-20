#!/usr/bin/env bash
# Removes the symlinks created by install-skills.sh from the global,
# per-user skill directories. Only removes a path if it is exactly a
# symlink pointing at this repo's skills/<name> — never touches
# unrelated files, directories, or symlinks to somewhere else.
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

echo "Skills to uninstall: ${skills[*]}"
echo
echo "Where should these be removed from?"
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

  removed=0
  skipped=0

  for name in "${skills[@]}"; do
    src="$skills_dir/$name"
    link="$target/$name"

    if [ -L "$link" ] && [ "$(readlink -f "$link")" = "$(readlink -f "$src")" ]; then
      rm "$link"
      echo "  OK   removed $link"
      removed=$((removed + 1))
    elif [ -e "$link" ] || [ -L "$link" ]; then
      echo "  SKIP $name: $link is not a symlink to this repo, leaving it alone"
      skipped=$((skipped + 1))
    fi
  done

  echo "  --"
  echo "  removed: $removed, skipped: $skipped"
done
