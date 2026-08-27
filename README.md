# AI-Native SDLC Skills

> **Code is no longer the bottleneck. The human-speed steps around it are.**
>
> — [Claude, *The AI-Native SDLC Playbook*, 2026](https://claude.com/blog/the-ai-native-sdlc-playbook)

A cross-platform implementation of the AI-Native SDLC playbook as
[Agent Skills](https://agentskills.io), for Claude Code, GitHub Copilot, OpenAI
Codex, and any other Agent Skills-compatible tool.

It ships as a package: **20 skills**, **artifact templates**, **subagent and
workflow templates**, **MCP client configs**, **governance hooks and managed
settings**, **eval examples**, an **indicator catalog**, and an `ai-dlc` CLI that
scaffolds, validates, and measures an AI-DLC project.

Zero runtime dependencies. `python3 scripts/validate.py` works in a fresh clone
with nothing installed.

## Table of contents

1. [The idea in one loop](#the-idea-in-one-loop)
2. [What is in this package](#what-is-in-this-package)
3. [Quick start](#quick-start)
4. [The `ai-dlc` CLI](#the-ai-dlc-cli)
5. [How a team should manage the AI-DLC](#how-a-team-should-manage-the-ai-dlc)
6. [The plays and the order to adopt them](#the-plays-and-the-order-to-adopt-them)
7. [Personas: who touches which skill](#personas-who-touches-which-skill)
8. [Measurement](#measurement)
9. [Governance](#governance)
10. [Two real flows](#two-real-flows)
11. [GitHub-centric fully immersed AI team](#github-centric-fully-immersed-ai-team)
12. [Repository layout](#repository-layout)
13. [Contributing](#contributing)

## The idea in one loop

In the traditional SDLC, every stage is a human gate. When AI agents can write
code in hours, that linear, document-and-handoff model becomes the bottleneck.

The AI-native SDLC reimagines the lifecycle as a loop where **each stage commits
an artifact the next stage can read**:

```
idea → intent.md → spec.md → plan.md → diff + tests → review → deploy → monitor
     ↑                                                             ↓
     └─────────────── close the loop ──────────────────────────────┘
```

The artifact chain is the audit trail: who asked for what, what the agent
produced, and who approved it. Humans stay accountable for judgment; agents
handle the mechanical work in between. (Claude, 2026)

Concretely, one intent is one folder and one branch:

```
intents/csv-export-20260826/
├── 01-intent.md      Plan      what is wanted, and why
├── 02-spec.md        Design    requirements, design, flagged concerns
├── 03-plan.md        Build     files that change, order, risks, proof
├── 04-review.md      Deploy    findings, plan fidelity, human decision
├── 05-deploy.md      Deploy    the gate, the rollout, the rollback
└── 06-lessons.md     Maintain  what changed in the agent's configuration
```

## What is in this package

**20 skills** across the six stages plus the cross-cutting plays:

| Stage | Skills |
|---|---|
| — | `00-onboarding` |
| Plan | `01-intent-capture` |
| Design | `02-spec-writer` |
| Build | `03-plan-mode`, `03-claude-md`, `03-subagents`, `03-parallel-sessions`, `03-org-skills` |
| Test | `04-feedback-loop`, `04-continuous-evals` |
| Deploy | `05-pr-review`, `05-release-gate`, `05-integration`, `05-cicd-triage`, `05-cicd-integration`, `05-managed-settings` |
| Maintain | `06-closing-the-loop`, `06-security-scan`, `06-on-call` |
| Cross-cutting | `platform-metrics` |

The prefix is the stage. `00` is onboarding and `01`–`06` are the six SDLC
stages the playbook defines. A play that is not a stage — measurement, tooling,
policy that applies throughout — carries the `platform-` prefix instead of a
number. **There is no seventh stage.**

Plus:

- **Artifact templates** — the six chain artifacts, `REVIEW.md`, `CLAUDE.md`,
  `AGENTS.md`, `bands.yaml`, `metrics.md`.
- **Subagent templates** — `verifier`, `simplifier`, `researcher`,
  `spec-auditor`, each with a tool allowlist and an output contract.
- **Workflow templates** — PR review, CI triage, eval gating, chain validation,
  and control-band detection as GitHub Actions.
- **Org policy skill templates** — security, API design, brand, UX patterns.
- **MCP client templates** — 17 servers, generated for Claude Code, Copilot/VS
  Code, and Codex.
- **Governance** — project settings, administrator-controlled managed settings
  with sandboxing, and six hooks including a deterministic control-band detector.
- **Indicator catalog** — every indicator the playbook names, machine-readable,
  with eight of them computed from your repository.

## Quick start

```bash
pip install -e .

# Validate the package (skills, MCP, hooks, templates, docs, artifact chain)
ai-dlc validate

# Install skills for your agent client
ai-dlc install claude

# Scaffold a new project, with the CI workflows
ai-dlc init-repo ./my-product --with-ci

# Then, from inside that project
ai-dlc backlog          # what is in flight and at which stage
ai-dlc metrics          # is the loop actually getting faster
ai-dlc adoption         # which play to adopt next
```

## The `ai-dlc` CLI

| Command | What it does |
|---|---|
| `ai-dlc validate` | Validates skills, MCP fragments, hooks, templates, examples, and that documented CLI commands exist |
| `ai-dlc install [client]` | Installs skills into `~/.claude/skills`, `~/.codex/skills`, `.agents/skills`, or `.github/skills` |
| `ai-dlc init-repo <path>` | Scaffolds the project layout, hooks, subagents, and templates |
| `ai-dlc migrate <path>` | Moves a project from the old flat layout to `intents/<id>/`; dry run by default |
| `ai-dlc backlog` | Reads `intents/` as a work queue, including intents that exist only on branches |
| `ai-dlc metrics` | Computes the locally derivable delivery indicators |
| `ai-dlc adoption` | Derives the play dependency graph and the rollout order |
| `ai-dlc mcp-sync` | Regenerates the per-client MCP configs |

Every command supports `--json`. `backlog` and `metrics` also support
`--markdown` for pasting into a PR.

## How a team should manage the AI-DLC

### 1. Version the skills next to the code

Skills are just markdown. Keep them in the product repo under `.claude/skills/`,
`.codex/skills/`, `.agents/skills/`, or `.github/skills/`. When a skill changes,
it goes through the same PR review as the code.

### 2. Use the artifact chain as your source of truth

Each stage produces a committed artifact. Keep them in git so the chain is the
audit trail. If your organization already uses Jira or ServiceNow, the Markdown
artifacts can be working copies linked by record ID, or the legacy system can be
the source of truth with MCP writes in each session. (Claude, 2026)

Whichever you choose, **write it down** — see `references/roles.md`. The failure
mode is not choosing, and maintaining two half-complete records.

### 3. Encode institutional knowledge as skills, not habits

Policy-owned knowledge goes in `skills/`, project context in `CLAUDE.md`, one-off
prompts in the chat. `03-org-skills` and `templates/skills/` are the starting
point, and the test for a good rule is simple: an agent must be able to check it.
"Follow security best practices" changes nothing. "Never log a field named `ssn`,
`email`, `phone`, or `name`" changes behaviour.

### 4. Put the human at the gates, not the critical path

Agents handle capture, drafting, testing, triage, and first-pass review. Humans
approve the intent, sign off the spec, accept the plan, merge the PR, and
authorize production. Hooks make the gates deterministic — including
`no-self-approve.sh`, which stops the agent that wrote the code from approving
it.

### 5. Connect to existing tools over MCP

Slack, Jira, GitHub, Figma, Datadog, PagerDuty and the rest are connected, not
replaced. Provide your tokens; the templates point at official endpoints.

### 6. Regression-test your agent configuration

`CLAUDE.md`, skills, hooks, and MCP setup steer the agent, so they get the same
regression testing as code. `04-continuous-evals` builds the suite;
`templates/workflows/ai-dlc-evals.yml` runs it when configuration changes.

## The plays and the order to adopt them

Some plays have no prerequisites; others quietly assume one. The graph lives in
each skill's `metadata.requires`, so it is one source of truth:

```bash
ai-dlc adoption
```

**Start today, in any order:** `01-intent-capture`, `03-claude-md`,
`03-org-skills`, `05-release-gate`.

`03-claude-md` is the highest-leverage of the four — almost everything downstream
improves when the agent knows how the repository actually works, and little of it
works well while the agent does not.

The full order, the signals that you moved too fast, and the signals that you are
ready for the next play are in `references/adoption.md`.

## Personas: who touches which skill

| Persona | Skill | MCP servers | Artifact |
|---|---|---|---|
| PM | `01-intent-capture` | Slack, Intercom, Jira, Notion, Monday | `01-intent.md` |
| Designer | `02-spec-writer` | Figma, Notion, Confluence | `02-spec.md` |
| Engineer | `03-plan-mode` | GitHub, GitLab | `03-plan.md` |
| Engineer | `03-subagents`, `03-parallel-sessions` | — | `.claude/agents/` |
| Policy owner | `03-org-skills` | Notion, Confluence | `skills/` |
| QA / Test | `04-continuous-evals` | Playwright, GitHub | `evals/` |
| Tech lead | `05-pr-review` | GitHub, GitLab | `04-review.md` |
| Release manager | `05-release-gate` | GitHub, Vercel | `05-deploy.md`, hooks |
| Platform engineer | `03-claude-md`, `05-managed-settings`, `05-cicd-integration` | GitHub, GitLab | `CLAUDE.md`, settings, workflows |
| SRE | `06-closing-the-loop` | Datadog, PagerDuty, Slack | `01-intent.md`, `bands.yaml` |
| Security | `06-security-scan` | Sentry, GitHub, Jira | `01-intent.md` / PR |
| Tech lead / Platform | `platform-metrics` | GitHub, Datadog | `metrics/` |

Who decides what, and which decisions an agent must never make, is in
`references/roles.md`.

## Measurement

The playbook names about thirty leading and lagging indicators. This package is
explicit about which it can compute and which it cannot.

**Computed from your repository — eight indicators, no external API:**

```
$ ai-dlc metrics

INDICATOR                     VALUE  DETAIL
artifact-chain-completeness   42%    5/12 artifacts
time-to-intent                2.0h   n=1 of 2 intents
intent-survival ~             0%     0 landed · 1 open · 1 stale
intent-staleness              1      payment-audit-20260610 (78d)
stage-latency:intent->spec    24.0h  n=1 min 24.0h max 24.0h
spec-churn                    0      n=1
plan-diff-alignment           67%    planned 2 · matched 2 · unplanned 1
rework-after-review           1      n=1
```

`plan-diff-alignment` is the one to read first: it compares the paths under
`## Files that change` in `03-plan.md` against the actual diff on the intent
branch. It is the best local signal for scope creep and plan fidelity, and it is
safe to enforce because the cheap way to satisfy it is to keep the plan accurate.

**Everything else** — CI pass rates, PR review time, hook wait time, DORA,
security scan trends — needs an API this package does not talk to. Those are
reported as `n/a` with the owning system named, never estimated.
`references/metrics-catalog.md` lists all of them; `templates/metrics.md` has a
place to record them by hand.

`ai-dlc validate` enforces that this stays honest: an indicator cannot claim to be
computable without an implementation, and an implementation cannot exist without a
catalog entry.

## Governance

Three layers, in increasing order of authority — see `governance/README.md`.

| Hook | Blocks | Unblocked by |
|---|---|---|
| `production-gate.sh` | A production deploy | `RELEASE_APPROVAL` from a release manager |
| `migration-ticket.sh` | Schema, migration, infra changes | `CHANGE_TICKET` |
| `block-test-edit.sh` | Editing tests while fixing a bug | Unsetting `FIX_TASK`, in the open |
| `no-self-approve.sh` | `gh pr review --approve`, `gh pr merge`, force-push to main | Nothing — a human does it |
| `detect-bands.sh` | Nothing; it is the deterministic band detector | — |

Promotion from `integration` to `main` is human-only and deliberately absent
from every workflow template in this package. A gate an agent can satisfy is not
a gate.

> **`allowed-tools` is not a security control.** Claude Code enforces it; Codex,
> Copilot, and other Agent Skills clients ignore the field entirely. It is
> written for least privilege and it is useful, but the gates that actually hold
> are hooks, `permissions.deny`, the sandbox, and branch protection. Do not
> treat a skill's tool list as a boundary when the same skill is installed for a
> client that does not read it.

`governance/managed-settings.json` holds the administrator-controlled policy that
engineers cannot override: credential paths, self-approval, sandbox, network
allowlist, telemetry. `05-managed-settings` explains what belongs in which layer.

Every gate decision is appended to `.ai-dlc/audit.jsonl`, which works with no
collector and no vendor.

## Getting several intents to production

Once more than one intent lands per day, the constraint stops being review and
becomes **integration**. Anthropic reports that after code generation was
automated the bottleneck moved to "packaging releases in ways users can
understand, and to managing merge queues that are suddenly overwhelmed."

Per-PR CI cannot help with this. It answers *does this intent work against `main`
as it was when the branch was cut?* — not *do the six intents landing today work
together?*

```
intent/csv-export-20260826    ──┐
intent/rate-limit-20260827    ──┼──▶  integration  ──▶  main  ──▶  production
intent/audit-log-20260827     ──┘         │                │
                                          │                └─ promotion: human only
                                          └─ staging, validated as a set
```

| Branch | Meaning | Who moves it |
|---|---|---|
| `intent/<id>` | One intent, Build through Review. Short-lived. | The engineer's session |
| `integration` | Accepted but not promoted. Always deployed to staging, validated as a combination. | The merge queue |
| `main` | What production runs. | **A human, always** |

**Merge is not release.** Intents are not batched into a train. Each one reaches
production *dark* behind its own feature flag and ramps on its own schedule —
which is what Anthropic actually describes: most deployments use feature flags,
with Claude managing "canary traffic, monitoring for issues, and automatically
ramping a given feature flag up or down."

That buys four things: nothing waits for the slowest intent, blast radius is per
intent rather than per release, rollback is a flag flip instead of unpicking a
merge of six, and the human gate sits at the ramp where canary metrics exist
rather than at the merge where only a diff does.

`05-integration` is the play. `references/integration-branch.md` has the model,
the rationale, when *not* to run an integration branch, and the sources.

## Two real flows

### Startup: CSV export in an afternoon

1. A customer asks for CSV export in Intercom.
2. The PM runs `01-intent-capture`; the agent pulls the thread and writes
   `01-intent.md` with the `Signal at` timestamp.
3. The PM runs `02-spec-writer`; the agent pulls the Figma mock and writes
   `02-spec.md`.
4. The engineer runs `03-plan-mode`; the agent writes `03-plan.md` with files,
   order, and proof.
5. The agent implements; `04-feedback-loop` runs `npm test` and a Playwright
   screenshot; the `verifier` subagent confirms what actually passed.
6. `05-pr-review` tags a missing input-validation check and writes `04-review.md`.
   The engineer fixes it and merges.
7. `06-closing-the-loop` watches `vercel` and `sentry` after deploy.

Full example in `examples/startup-feature.md`.

### Enterprise: payment audit logging

1. `JIRA-4822` requires audit logging. `01-intent-capture` pulls the ticket and
   notes PCI/PII constraints.
2. `02-spec-writer` applies the security and compliance org skills, flags the
   audit requirements, and waits for the policy owner.
3. `03-plan-mode` writes `03-plan.md` and routes it for higher-risk sign-off.
4. Implementation runs under hooks: no `schema.sql` edit without `CHANGE_TICKET`.
5. `04-continuous-evals` adds a regression check for the new schema.
6. `05-pr-review` and `05-release-gate` run; production is blocked until the
   change-advisory board sets `RELEASE_APPROVAL`, recorded in `05-deploy.md`.
7. `06-security-scan` and `06-closing-the-loop` keep watching.

Full example in `examples/enterprise-change.md`. Persona guide in
`references/team-flows.md`.

## GitHub-centric fully immersed AI team

For a startup that wants GitHub to be the single source of truth, the repo is
both the backlog and the agent memory.

```
.
├── .claude/skills/          # skills from this package
├── .claude/agents/          # subagent definitions
├── .claude/hooks/           # governance hooks
├── CLAUDE.md                # agent memory
├── AGENTS.md
├── REVIEW.md                # review policy
├── bands.yaml               # control bands
├── intents/                 # the backlog
│   ├── csv-export-20260826/
│   │   ├── 01-intent.md ... 06-lessons.md
│   │   └── ...
│   └── payment-audit-20260827/
│       └── 01-intent.md
└── src/
```

One branch per intent (`intent/<id>`), one PR, a human merges when the chain is
accepted. `ai-dlc backlog` reads intents that exist only on unmerged branches, so
the queue is visible from `main`.

Full guide in `examples/github-centric-team.md`.

## Repository layout

```
.
├── skills/                 # canonical skill source (19 skills)
├── templates/              # artifacts, subagents, workflows, org policy skills
├── mcp/                    # per-server fragments and generated client configs
├── governance/             # hooks, project settings, managed settings
├── references/             # indicators, metrics catalog, adoption, roles, observability
├── examples/               # startup, enterprise, and GitHub-centric flows
├── evals/                  # example evals
├── ai_dlc/                 # the CLI and its modules
├── scripts/                # wrappers so the repo runs without installation
├── tests/                  # pytest
├── .claude-plugin/         # Claude Code plugin manifest
└── .github/workflows/      # CI and release
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Everything must pass `make validate` and
`make test`.

## License

Apache-2.0. See [LICENSE](LICENSE).

## Reference

Claude. (2026, August 21). *The AI-Native SDLC Playbook*.
https://claude.com/blog/the-ai-native-sdlc-playbook
