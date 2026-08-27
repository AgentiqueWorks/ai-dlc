# Governance

Three layers, in increasing order of authority. A setting at a higher layer wins.

| Layer | File | Owner | Engineers can override |
|---|---|---|---|
| Project | `settings.json` → `.claude/settings.json` | Tech lead, in the repo | Yes, via `.claude/settings.local.json` |
| User | `~/.claude/settings.json` | The engineer | — |
| Managed | `managed-settings.json` → the OS policy path | Platform / security, via MDM | **No** |

## What belongs where

- **Managed settings** hold the rules that must hold everywhere: no reading
  credentials, no approving your own pull request, no force-push to a default
  branch, sandbox on, telemetry on. Keep this file short. Every rule here is a
  rule nobody can turn off during an incident, which is the point and also the
  risk.
- **Project settings** hold the gates specific to this codebase: which paths are
  frozen, which commands need a ticket, which hooks run.
- **Hooks** hold decisions that are deterministic. If a gate needs judgement, it
  is not a hook — it is a human at a gate.

## Hooks in this directory

| Hook | Blocks | Unblocked by |
|---|---|---|
| `production-gate.sh` | A production deploy command | `RELEASE_APPROVAL` set by a release manager |
| `migration-ticket.sh` | Schema, migration, and infra changes | `CHANGE_TICKET` set to an approved record |
| `block-test-edit.sh` | Editing tests while fixing a bug | Unsetting `FIX_TASK` and saying so in the PR |
| `no-self-approve.sh` | `gh pr review --approve`, `gh pr merge`, force-push to main | Nothing — a human does it |
| `detect-bands.sh` | Nothing; it is the control-band detector | — |
| `_lib.sh` | Shared helpers | — |

`_lib.sh` exists because of a real failure mode: a hook that reads stdin twice
gets an empty string the second time and silently stops gating anything. Read it
once, through `read_payload`.

## Keep hooks fast

A hook runs before every matching tool call. Anything slower than a few hundred
milliseconds belongs in CI. Measure `hook-wait-time` (see
`references/observability.md`) — a gate nobody can afford to wait for is a gate
somebody will disable.

## The audit trail

`_lib.sh` appends every gate decision to `.ai-dlc/audit.jsonl`. Combined with the
committed artifact chain and the PR thread, that is the record of who asked for
what, what the agent produced, and who approved it. Add `.ai-dlc/audit.jsonl` to
your log shipping, not to `.gitignore`, if you need it for compliance.
