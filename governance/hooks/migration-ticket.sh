#!/usr/bin/env bash
# Blocks edits to migration/schema/infra files without a change ticket.

set -euo pipefail

tool=$(jq -r '.tool_name' < /dev/stdin 2>/dev/null || echo "")
input=$(jq -r '.tool_input.path // .tool_input.old_string // ""' < /dev/stdin 2>/dev/null || echo "")

if [ "$tool" = "Edit" ] || [ "$tool" = "Bash" ]; then
  if [[ "$input" == *"migrations/"* || "$input" == *"schema"* || "$input" == *"infra/"* ]]; then
    if [ -z "${CHANGE_TICKET:-}" ]; then
      echo "Edits to migrations, schema, or infra require CHANGE_TICKET." >&2
      exit 2
    fi
  fi
fi

exit 0