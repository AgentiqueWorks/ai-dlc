#!/usr/bin/env bash
# Blocks edits to test files when the agent is in a fix task so it
# cannot weaken the check on the code it is fixing.

set -euo pipefail

tool=$(jq -r '.tool_name' < /dev/stdin 2>/dev/null || echo "")
input=$(jq -r '.tool_input.old_string // .tool_input.path // ""' < /dev/stdin 2>/dev/null || echo "")

if [ "$tool" = "Edit" ] && [[ "$input" == *"test"* || "$input" == *"spec"* ]]; then
  if [ "${FIX_TASK:-}" = "1" ]; then
    echo "Test/spec files cannot be edited while FIX_TASK=1." >&2
    echo "Fix the code, not the test." >&2
    exit 2
  fi
fi

exit 0