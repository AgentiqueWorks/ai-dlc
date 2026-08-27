#!/usr/bin/env bash
# No production deploy without an authorization from the release manager.
# The approval is a token the agent cannot mint for itself.

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"
read_payload

cmd="$(command_string)"
[ -n "$cmd" ] || exit 0

looks_like_deploy=0
case "$cmd" in
  *deploy*|*"release "*|*"vercel --prod"*|*"kubectl rollout"*|*"helm upgrade"*) looks_like_deploy=1 ;;
esac
looks_like_prod=0
case "$cmd" in
  *production*|*prod*|*--prod*|*live*) looks_like_prod=1 ;;
esac

if [ "$looks_like_deploy" = "1" ] && [ "$looks_like_prod" = "1" ]; then
  if [ -z "${RELEASE_APPROVAL:-}" ]; then
    deny \
      "Blocked: production deploy without a release authorization." \
      "A release manager sets RELEASE_APPROVAL to the sign-off id." \
      "The agent that wrote the change cannot authorize its own release."
  fi
  audit "allow" "production deploy authorized by ${RELEASE_APPROVAL}"
fi

exit 0
