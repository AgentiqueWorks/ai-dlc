#!/usr/bin/env bash
# Separation of duties: the agent that wrote the code cannot approve or merge it.
# Review findings are advisory; the decision belongs to a human code owner.

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh"
read_payload

cmd="$(command_string)"
[ -n "$cmd" ] || exit 0

case "$cmd" in
  *"gh pr review"*"--approve"*|*"gh pr merge"*|*"glab mr approve"*|*"glab mr merge"*)
    deny \
      "Blocked: agents do not approve or merge pull requests." \
      "Write findings to intents/<id>/04-review.md and post them as a comment." \
      "A human code owner approves through branch protection."
    ;;
  *"git push"*"--force"*|*"git push"*"-f "*)
    case "$cmd" in
      *main*|*master*)
        deny "Blocked: force-push to the default branch." ;;
    esac
    ;;
esac

exit 0
