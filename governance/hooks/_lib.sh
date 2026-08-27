#!/usr/bin/env bash
# Shared helpers for AI-DLC PreToolUse hooks.
#
# A hook receives the pending tool call on stdin as JSON, exactly once. Reading
# stdin twice yields an empty string the second time, which silently disables
# the gate — so every hook reads it once, here, into PAYLOAD.

set -euo pipefail

read_payload() {
  PAYLOAD="$(cat)"
  # Record the calling hook now: inside deny()/audit() the caller frame is
  # _lib.sh itself, which would make every log line say "_lib.sh".
  HOOK_NAME="$(basename "${BASH_SOURCE[1]:-unknown}")"
  export PAYLOAD HOOK_NAME
}

# field <jq-expression> [default]
field() {
  local expr="$1" default="${2:-}"
  if ! command -v jq >/dev/null 2>&1; then
    echo "$default"
    return 0
  fi
  printf '%s' "$PAYLOAD" | jq -r "$expr // \"$default\"" 2>/dev/null || echo "$default"
}

tool_name() { field '.tool_name'; }

# Every path-shaped field a tool might carry, newline separated.
target_paths() {
  field '[.tool_input.file_path, .tool_input.path, .tool_input.notebook_path, .tool_input.pattern] | map(select(. != null)) | join("\n")'
}

command_string() { field '.tool_input.command'; }

# deny <reason...> — block the call and tell the agent why.
deny() {
  printf '%s\n' "$@" >&2
  audit "deny" "$*"
  exit 2
}

# audit <decision> <reason> — append one line to the local decision log so the
# gate leaves a record even when nothing is blocked.
audit() {
  local dir="${CLAUDE_PROJECT_DIR:-.}/.ai-dlc"
  local log="$dir/audit.jsonl"
  mkdir -p "$dir" 2>/dev/null || return 0
  printf '{"at":"%s","hook":"%s","tool":"%s","decision":"%s","reason":%s}\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    "${HOOK_NAME:-unknown}" \
    "$(tool_name)" \
    "$1" \
    "$(printf '%s' "${2:-}" | sed 's/\\/\\\\/g; s/"/\\"/g; s/^/"/; s/$/"/')" \
    >> "$log" 2>/dev/null || true
}
