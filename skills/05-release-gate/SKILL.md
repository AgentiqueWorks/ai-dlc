---
name: 05-release-gate
description: Encode human approval gates as deterministic hooks that run before the agent can act on sensitive operations. Use for release, migration, and protected-path gating.
---

# Release gate

## Job

Make approval gates enforceable at the moment the agent tries to act.

## Steps

1. List the gates that must survive (release authorization, change ticket, protected paths).
2. For each gate, create a script in `.claude/hooks/` or `.claude/settings.json` that allows, asks, or blocks the action.
3. A block must explain the reason and the route to approval.
4. Keep gate checks fast; heavy checks belong at the PR or CI level.
5. Document the approval condition (e.g. an env var, a ticket, a code-owner sign-off).

## Output

- Hook scripts and `settings.json` snippets.
- Clear error messages when a gate is triggered.