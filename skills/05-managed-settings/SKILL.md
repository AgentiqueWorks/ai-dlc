---
name: 05-managed-settings
description: Configure administrator-controlled permissions, sandboxing, and network allowlists that engineers cannot override, so the rules that must hold everywhere actually do. Use when rolling agents out beyond one team.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Edit
  - Bash(git status:*)
  - Bash(git add:*)
  - Bash(git commit:*)
metadata:
  stage: "05-deploy"
  persona: "platform, security, tech-lead"
  requires: "05-release-gate"
  produces: ".claude/settings.json"
  indicators: "gate-violations, hook-wait-time"
  mcp: ""
  maturity: "beta"
---

# Managed settings and sandboxing

## Job

Separate the rules an engineer may adjust from the rules nobody may, and enforce
the second set at the operating system rather than in a prompt.

## Who uses this

- **Platform engineers** rolling agents out across teams.
- **Security leads** who need a control that survives an incident at 2am.
- **Tech leads** deciding what belongs in the repo versus in policy.

## Three layers

| Layer | File | Owner | Overridable |
|---|---|---|---|
| Project | `.claude/settings.json` | Tech lead, in the repo | Yes, locally |
| User | `~/.claude/settings.json` | The engineer | — |
| Managed | the OS policy path | Platform / security, via MDM | **No** |

`governance/README.md` has the file this package ships as a starting point;
`references/settings-precedence.md` has the exact policy path per platform, the
full precedence order, and the one question that settles which layer a rule
belongs in.

## Example prompts

- "What should be in managed settings versus project settings for us?"
- "Set up a network allowlist so sessions can reach our registry and nothing else."
- "Our sandbox blocks the test suite. Is the sandbox wrong or is the test suite?"

## Steps

1. **Sort the rules into layers.** Ask one question per rule: would you accept an
   engineer turning this off during an incident? If no, it is managed. Everything
   else is project settings, where it can be argued with in a PR.
2. **Keep managed settings short.** Credentials, destructive commands, separation
   of duties, sandbox on, telemetry on. A long managed file becomes the file
   everyone fights, and the fight ends with an exception process that defeats it.
3. **Deny credential paths explicitly**, not by convention: `.env`, `secrets/`,
   `*.pem`, `~/.aws`, `~/.ssh`. `deny` beats `allow`, so this holds even when a
   project loosens its own settings.
4. **Enable the sandbox with a domain allowlist.** Start from the endpoints the
   work actually needs — the model API, your forge, your package registries — and
   add on evidence, not on request. Record why each domain is on the list.
5. **Encode separation of duties as a deny, not a norm.**
   `Bash(gh pr review --approve:*)` and `Bash(gh pr merge:*)` belong in managed
   settings: the agent that wrote the change must not be able to approve it, even
   if a project's settings say otherwise.
6. **Turn on telemetry** (`CLAUDE_CODE_ENABLE_TELEMETRY`, OTLP exporters) so gate
   decisions and hook wait times are measurable. See
   `references/observability.md`.
7. **Test the sandbox against the real test suite** before rolling out. A sandbox
   that blocks the build gets disabled by everyone within a day. If the suite
   needs a domain, add it deliberately; if it needs the whole internet, that is a
   finding about the test suite.
8. **Give exceptions an owner and an expiry.** Route them through the same PR
   process as everything else, and re-review on the expiry date.

## What this does not do

Managed settings stop tool calls. They do not stop bad judgement, and they are
not a substitute for review. Anything requiring judgement stays with a human at a
gate — that is `05-release-gate`.

## Output

- A managed settings file deployed by MDM, holding only non-overridable rules.
- A project `.claude/settings.json` holding the repository's own gates.
- A sandbox network allowlist with a recorded reason per domain.
- An exception register with owners and expiry dates.

## Measure

| Indicator | Type | Where it comes from |
|---|---|---|
| `gate-violations` | lagging | an external system |
| `hook-wait-time` | leading | an external system |

Compare `gate-violations` before and after each control ships. Watch
`hook-wait-time` at the same time: a control nobody can afford to wait for is a
control somebody will route around.

See `references/metrics-catalog.md` and `references/observability.md`.
