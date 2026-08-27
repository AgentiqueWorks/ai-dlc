#!/usr/bin/env bash
# Schema, migration, and infrastructure changes need a change ticket. This is a
# deterministic gate, not a judgement call: the agent cannot argue with it.

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"
read_payload

needs_ticket=0

while IFS= read -r path; do
  [ -n "$path" ] || continue
  case "$path" in
    *migrations/*|*migration/*|*schema*|*infra/*|*terraform/*|*.tf|*helm/*|*k8s/*)
      needs_ticket=1
      target="$path"
      ;;
  esac
done <<< "$(target_paths)"

cmd="$(command_string)"
case "$cmd" in
  *"migrate"*|*"terraform apply"*|*"kubectl apply"*|*"alembic upgrade"*)
    needs_ticket=1
    target="$cmd"
    ;;
esac

if [ "$needs_ticket" = "1" ] && [ -z "${CHANGE_TICKET:-}" ]; then
  deny \
    "Blocked: ${target:-this change} touches schema, migrations, or infrastructure." \
    "Set CHANGE_TICKET to the approved change-record id before retrying." \
    "Record the ticket in intents/<id>/05-deploy.md under Gate."
fi

audit "allow" "${target:-no migration target}"
exit 0
