#!/usr/bin/env bash
# First-pass verification: while fixing a bug, the agent must not be able to
# weaken the test that proves the bug is gone.
#
# Set FIX_TASK=1 for the session that is fixing a failing test.

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"
read_payload

[ "${FIX_TASK:-}" = "1" ] || exit 0

case "$(tool_name)" in
  Edit|Write|NotebookEdit|MultiEdit) ;;
  *) exit 0 ;;
esac

while IFS= read -r path; do
  [ -n "$path" ] || continue
  case "$path" in
    *test*|*spec*|*Test*|*_test.*|*.test.*|*.spec.*)
      deny \
        "Blocked: $path is a test file and FIX_TASK=1." \
        "Fix the code so the test passes. If the test itself is wrong, unset" \
        "FIX_TASK and say so explicitly in the pull request."
      ;;
  esac
done <<< "$(target_paths)"

exit 0
