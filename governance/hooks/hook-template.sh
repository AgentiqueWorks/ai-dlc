#!/usr/bin/env bash
# Template for a new AI-DLC gate.
#
# Contract:
#   - stdin carries the pending tool call as JSON, and can only be read once.
#     `read_payload` does that for you and puts it in $PAYLOAD.
#   - exit 0 allows the call, exit 2 blocks it and shows stderr to the agent.
#   - Keep hooks fast. They run before every matching tool call, so anything
#     slower than a few hundred milliseconds belongs in CI, not here.
#   - A hook is a deterministic gate. If the decision needs judgement, it is not
#     a hook — it is a human at a gate.

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"
read_payload

# tool="$(tool_name)"
# cmd="$(command_string)"
# paths="$(target_paths)"

# if [ "$tool" = "Bash" ] && [[ "$cmd" == *"something dangerous"* ]]; then
#   deny "Blocked: <what and why>." "<what the human should do instead>"
# fi

exit 0
