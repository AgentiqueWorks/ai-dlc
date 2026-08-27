#!/usr/bin/env bash
# Blocks any Bash command that looks like a production deploy unless
# RELEASE_APPROVAL is set.

set -euo pipefail

cmd=$(jq -r '.tool_input.command' < /dev/stdin 2>/dev/null || echo "")

if [[ "$cmd" == *"deploy"* && "$cmd" == *"production"* ]]; then
  if [ -z "${RELEASE_APPROVAL:-}" ]; then
    echo "Production deploys need a release authorization." >&2
    echo "Set RELEASE_APPROVAL to the change-ticket or sign-off ID." >&2
    exit 2
  fi
fi

exit 0