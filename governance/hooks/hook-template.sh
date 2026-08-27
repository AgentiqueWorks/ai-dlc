#!/usr/bin/env bash
# Template for a new Claude Code hook.
# Hooks receive the pending tool call on stdin as JSON.

set -euo pipefail

tool_name=$(jq -r '.tool_name' < /dev/stdin 2>/dev/null || echo "")
tool_input=$(jq -r '.tool_input // {}' < /dev/stdin 2>/dev/null || echo "")

# Example: block a specific tool
# if [ "$tool_name" = "Bash" ]; then
#   echo "Bash is blocked by this hook." >&2
#   exit 2
# fi

exit 0