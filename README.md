# AI-Native SDLC Skills

> **Code is no longer the bottleneck. The human-speed steps around it are.**
>
> — [Claude, *The AI-Native SDLC Playbook*, 2026](https://claude.com/blog/the-ai-native-sdlc-playbook)

This repository is a cross-platform set of [Agent Skills](https://agentskills.io) that turns the AI-Native SDLC playbook into version-controlled, reusable workflows for Claude Code, GitHub Copilot, OpenAI Codex, and any other Agent Skills-compatible tool.

It ships as a package: **skills**, **artifact templates**, **MCP client configs**, **governance hooks**, **eval examples**, and a small `ai-dlc` CLI that can scaffold and validate an AI-DLC project.

## Table of contents

1. [The idea in one loop](#the-idea-in-one-loop)
2. [What is in this package](#what-is-in-this-package)
3. [Quick start](#quick-start)
4. [How a team should manage the AI-DLC](#how-a-team-should-manage-the-ai-dlc)
5. [Personas: who touches which skill](#personas-who-touches-which-skill)
6. [Two real flows](#two-real-flows)
7. [Governance hooks](#governance-hooks)
8. [The `ai-dlc` CLI](#the-ai-dlc-cli)
9. [Repository layout](#repository-layout)
10. [GitHub-centric fully immersed AI team](#github-centric-fully-immersed-ai-team)
11. [Contributing](#contributing)

## The idea in one loop

In the traditional SDLC, every stage is a human gate. When AI agents can write code in hours, that linear, document-and-handoff model becomes the bottleneck.

The AI-native SDLC reimagines the lifecycle as a loop where **each stage commits an artifact the next stage can read**:

```
idea → intent.md → spec.md → plan.md → diff + tests → review → deploy → monitor
     ↑                                                             ↓
     └─────────────── close the loop ──────────────────────────────┘
```

The artifact chain is the audit trail: who asked for what, what the agent produced, and who approved it. Humans stay accountable for judgment; agents handle the mechanical work in between. (Claude, 2026)

This repo gives your team the skills, templates, governance, and tool integrations to run that loop.

## What is in this package

- **13 skills** covering all six SDLC stages plus onboarding:
  - `00-onboarding` — start here
  - `01-intent-capture` — Plan
  - `02-spec-writer` — Design
  - `03-plan-mode` — Build
  - `03-claude-md` — Build
  - `04-feedback-loop` — Test
  - `04-continuous-evals` — Test
  - `05-pr-review` — Deploy
  - `05-release-gate` — Deploy
  - `05-cicd-triage` — Deploy
  - `06-closing-the-loop` — Maintain
  - `06-security-scan` — Maintain
  - `06-on-call` — Maintain
- **Artifact templates**: `intent.md`, `spec.md`, `plan.md`, `REVIEW.md`, `CLAUDE.md`, `bands.yaml`.
- **MCP client templates**: 17 servers including GitHub, Jira, Slack, Monday, Figma, Notion, Confluence, Linear, GitLab, Datadog, Sentry, PagerDuty, Vercel, Google Workspace, Stripe, Intercom, and Playwright.
- **Governance hooks and settings**: production gate, test-file protection, migration-ticket check, and a `.claude/settings.json` template.
- **Eval examples**: `evals/example-csv-export.*` and `evals/example-payment-audit.*`.
- **Install and validation tooling**: `ai-dlc` CLI, `scripts/install.sh`, `scripts/validate.py`, `Makefile`, and a GitHub Actions workflow.
- **Claude Code plugin manifest**: `.claude-plugin/plugin.json`.

## Quick start

```bash
pip install -e .

# Validate the package
ai-dlc validate

# Install skills for Claude Code
ai-dlc install claude

# Or scaffold a new project
ai-dlc init-repo ./my-product --client claude

# Regenerate combined MCP configs after editing mcp/configs/
ai-dlc mcp-sync
```

## How a team should manage the AI-DLC

### 1. Version the skills next to the code

Skills are just markdown. Keep them in the product repo under `.claude/skills/`, `.codex/skills/`, `.agents/skills/`, or `.github/skills/`. When a skill changes, it goes through the same PR review as the code. This keeps the agent's instructions auditable and aligned with policy.

### 2. Use the artifact chain as your source of truth

Each stage produces a committed artifact:

- `intent.md` — what is wanted and why
- `spec.md` — requirements, design, and flagged concerns
- `plan.md` — files that change, order of work, risks, proof
- the diff and its tests — the actual implementation
- `REVIEW.md` findings — the review record
- `bands.yaml` / `intent.md` — production feedback

Do not keep these in tickets or wikis. Keep them in git so the chain is the audit trail. If your organization already uses Jira or ServiceNow, the Markdown artifacts can be working copies linked by record ID, or the legacy system can be the source of truth with MCP writes in each session. (Claude, 2026)

### 3. Encode institutional knowledge as skills, not habits

A skill is how an organization makes its rules operational: security standards, API conventions, brand rules, UX patterns. Put policy-owned knowledge in `skills/`, keep project context in `CLAUDE.md`, and reserve one-off prompts for the chat. When the policy changes, the skill changes; the next session picks it up automatically.

### 4. Put the human at the gates, not the critical path

Agents should handle capture, drafting, testing, triage, and first-pass review. Humans approve the `intent.md`, sign off the `spec.md`, accept the `plan.md`, merge the PR, and authorize production. Use hooks for deterministic gates (e.g. no production deploy without `RELEASE_APPROVAL`) and keep deterministic checks in CI, not in the model.

### 5. Connect to existing tools over MCP

Slack, Jira, GitHub, Figma, Datadog, PagerDuty, and the rest are not replaced; they are connected. Use the provided MCP client templates to let the agent read tickets, pull mocks, post updates, query metrics, and deploy under the same human approval gates. The templates point to official remote endpoints or well-known community packages; you only need to provide your tokens.

### 6. Regression-test your agent configuration

`CLAUDE.md`, skills, hooks, and MCP setup steer the agent. They deserve the same regression testing as code. Use the `04-continuous-evals` skill to build an eval suite and run it in CI whenever configuration changes.

## Personas: who touches which skill

| Persona | Skill | MCP servers | Artifact |
|---|---|---|---|
| PM | `01-intent-capture` | Slack, Intercom, Jira, Notion, Monday | `intent.md` |
| Designer | `02-spec-writer` | Figma, Notion, Confluence | `spec.md` |
| Engineer | `03-plan-mode` | GitHub, GitLab | `plan.md` |
| QA / Test | `04-continuous-evals` | Playwright, GitHub | `evals/` |
| Tech lead | `05-pr-review` | GitHub, GitLab | review findings |
| Release manager | `05-release-gate` | GitHub, Vercel | `settings.json` / hooks |
| SRE | `06-closing-the-loop` | Datadog, PagerDuty, Slack | `intent.md` |
| Security | `06-security-scan` | Sentry, GitHub, Jira | `intent.md` / PR |
| Platform engineer | `03-claude-md` | GitHub, GitLab | `CLAUDE.md` |

## Two real flows

### Startup: CSV export in an afternoon

1. A customer asks for CSV export in Intercom.
2. The PM runs `01-intent-capture`; the agent pulls the Intercom thread and writes `intent.md`.
3. The PM runs `02-spec-writer`; the agent pulls the Figma mock and writes `spec.md`.
4. The engineer runs `03-plan-mode`; the agent writes `plan.md` with the files, order, and proof.
5. The agent implements, and `04-feedback-loop` runs `npm test` and a Playwright screenshot.
6. `05-pr-review` tags a missing input-validation check; the engineer fixes it and merges.
7. `06-closing-the-loop` watches `vercel` and `sentry` after deploy.

See the full example in `examples/startup-feature.md`.

### Enterprise: payment audit logging

1. `JIRA-4822` requires audit logging. `01-intent-capture` pulls the Jira ticket and notes PCI/PII constraints.
2. `02-spec-writer` applies security and compliance skills, flags the audit requirements, and waits for the policy owner.
3. `03-plan-mode` writes `plan.md` and routes it for higher-risk sign-off.
4. Implementation runs under hooks: no `schema.sql` edit without a change-ticket number.
5. `04-continuous-evals` adds a regression check for the new schema.
6. `05-pr-review` and `05-release-gate` run; production is blocked until the change-advisory board sets `RELEASE_APPROVAL`.
7. `06-security-scan` and `06-closing-the-loop` keep watching.

See the full example in `examples/enterprise-change.md`.

For the full persona guide, read `references/team-flows.md`.

## GitHub-centric fully immersed AI team

For a startup that wants GitHub to be the single source of truth, the repo itself becomes the backlog and the agent memory.

### Layout

```
.
├── .claude/skills/          # skills from this package
├── .claude/hooks/           # governance hooks
├── CLAUDE.md                # agent memory
├── AGENTS.md
├── intents/                 # the backlog
│   ├── csv-export-20260826/
│   │   ├── 01-intent.md
│   │   ├── 02-spec.md
│   │   ├── 03-plan.md
│   │   ├── 04-review.md
│   │   ├── 05-deploy.md
│   │   └── 06-lessons.md
│   └── payment-audit-20260827/
│       └── 01-intent.md
└── src/
```

### One branch per intent

```
main
  └── intent/csv-export-20260826
```

A single branch per intent keeps the startup lean. The branch accumulates the numbered artifacts in `intents/<id>/` plus the code. One PR is opened and a human merges it when the full chain is accepted.

### Flow

1. **PM** runs `01-intent-capture`. The agent creates branch `intent/csv-export-20260826`, writes `intents/csv-export-20260826/01-intent.md`, and opens a draft PR.
2. **PM/Designer** runs `02-spec-writer`. The agent writes `02-spec.md` in the same folder.
3. **Engineer** runs `03-plan-mode`. The agent writes `03-plan.md` and then implements the code.
4. **Agent** runs `04-feedback-loop`, then `05-pr-review` writes `04-review.md`.
5. **Tech lead** reviews and merges to `main`.
6. **SRE** runs `06-closing-the-loop` after deploy. Any finding writes a new `intents/<id>/01-intent.md` and starts the loop again.

See the full guide in `examples/github-centric-team.md` and sample intent folders in `examples/intents/`.

## Governance hooks

The `governance/` directory contains hook examples and a `.claude/settings.json` template:

- `hooks/production-gate.sh` — blocks `*deploy*production*` unless `RELEASE_APPROVAL` is set.
- `hooks/block-test-edit.sh` — blocks test/spec edits while `FIX_TASK=1`.
- `hooks/migration-ticket.sh` — blocks migration/schema/infra edits without `CHANGE_TICKET`.

Use `make init-repo` to copy these into a new project's `.claude/hooks/`.

## The `ai-dlc` CLI

```bash
ai-dlc validate          # validate all skills and MCP configs
ai-dlc install claude    # install skills for Claude Code
ai-dlc init-repo ./app   # scaffold a new project
ai-dlc mcp-sync          # regenerate combined mcp.json files
```

## Repository layout

```
.
├── skills/                 # canonical skill source
├── templates/              # SDLC artifact templates
├── mcp/                    # MCP client templates
├── governance/             # hooks and managed settings
├── references/             # MCP catalog and team-usage flows
├── examples/               # startup and enterprise examples
├── evals/                  # example evals
├── ai_dlc/                 # Python CLI
├── scripts/                # install, validate, init-repo, mcp-sync
├── tests/                  # pytest validation
├── .claude-plugin/         # Claude Code plugin manifest
├── .github/workflows/      # CI and release
├── AGENTS.md               # cross-client agent onboarding
├── CLAUDE.md               # Claude Code project context
├── .github/copilot-instructions.md
└── pyproject.toml
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache-2.0. See [LICENSE](LICENSE).

## Reference

Claude. (2026, August 21). *The AI-Native SDLC Playbook*. https://claude.com/blog/the-ai-native-sdlc-playbook