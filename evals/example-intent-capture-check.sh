#!/usr/bin/env bash
# Eval check for intent capture.
#
# Asserts the shape the rest of the loop depends on: the folder convention, the
# Signal at field that time-to-intent needs, and that capture did not turn into
# implementation.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

intent="$(ls -d intents/*dark*mode*/ 2>/dev/null | head -1 || true)"
[ -n "$intent" ] || { echo "No intents/<id>/ folder was created for the request"; exit 1; }

[ -f "${intent}01-intent.md" ] || { echo "Missing ${intent}01-intent.md"; exit 1; }

# time-to-intent is unmeasurable without this field, so the skill must fill it in.
grep -q '\*\*Signal at:\*\*[[:space:]]*2026-09-01T08:15:00Z' "${intent}01-intent.md" \
  || { echo "01-intent.md is missing the Signal at timestamp from the source"; exit 1; }

# Every section the template requires must be present and filled.
for heading in "## Problem" "## Proposed outcome" "## Constraints" "## Open questions"; do
  grep -q "^${heading}$" "${intent}01-intent.md" || { echo "Missing section: ${heading}"; exit 1; }
done
grep -q '^<.*>$' "${intent}01-intent.md" && { echo "Template placeholders were left unfilled"; exit 1; }

# Capture is not implementation.
[ -f "${intent}03-plan.md" ] && { echo "Capture wrote a plan; it should stop at the intent"; exit 1; }
if git rev-parse --git-dir >/dev/null 2>&1; then
  changed="$(git diff --name-only HEAD -- . ':(exclude)intents/**' | head -1)"
  [ -z "$changed" ] || { echo "Capture modified code outside intents/: ${changed}"; exit 1; }
fi

echo "Intent capture eval passed"
