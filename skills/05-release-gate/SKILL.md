---
name: 05-release-gate
description: Encode human approval gates as deterministic hooks that run before the agent can act on sensitive operations. Use for release, migration, and protected-path gating.
---

# Release gate

## Job

Make approval gates enforceable at the moment the agent tries to act.

## Who uses this

- **Release managers** who need a sign-off before production deploys.
- **Security / compliance engineers** protecting migrations, schemas, and secrets.
- **Platform engineers** configuring `CLAUDE.md` and hooks.

## Example prompts

- "Create a hook that blocks any deploy command to production without RELEASE_APPROVAL."
- "Require a change-ticket number before the agent can edit a database migration."
- "Add a hook that runs the formatter after every file edit."

## Steps

1. List the gates that must survive (release authorization, change ticket, protected paths, test-file edits).
2. For each gate, create a hook in `.claude/hooks/` or an entry in `.claude/settings.json`.
3. A hook can allow, ask, or block. A block must explain the reason and the route to approval.
4. Keep hook execution fast; heavy checks belong in CI or the PR.
5. Document the approval condition (env var, ticket field, code-owner sign-off).

## Output

- Hook scripts and `settings.json` snippets.
- Clear error messages when a gate is triggered.