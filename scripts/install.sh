#!/usr/bin/env bash
set -euo pipefail

CLIENT="${1:-${INSTALL_CLIENT:-claude}}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

case "$CLIENT" in
  claude)
    TARGET="$HOME/.claude/skills"
    ;;
  codex)
    TARGET="$HOME/.codex/skills"
    ;;
  agents)
    TARGET="$REPO_ROOT/.agents/skills"
    ;;
  github)
    TARGET="$REPO_ROOT/.github/skills"
    ;;
  *)
    echo "Unknown client: $CLIENT" >&2
    echo "Usage: $0 [claude|codex|agents|github]" >&2
    exit 1
    ;;
esac

mkdir -p "$TARGET"

for skill in "$REPO_ROOT"/skills/*/; do
  name="$(basename "$skill")"
  dest="$TARGET/$name"
  rm -rf "$dest"
  cp -R "$skill" "$dest"
  echo "Installed $name -> $dest"
done

echo "Skills installed for $CLIENT at $TARGET"