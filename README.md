# AI-Native SDLC Skills

> **Code is no longer the bottleneck. The human-speed steps around it are.**
>
> — [Claude, *The AI-Native SDLC Playbook*, 2026](https://claude.com/blog/the-ai-native-sdlc-playbook)

This repository is a cross-platform set of [Agent Skills](https://agentskills.io) that turns the AI-Native SDLC playbook into version-controlled, reusable workflows for Claude Code, GitHub Copilot, OpenAI Codex, and any other Agent Skills-compatible tool.

It is not another framework. It is a **set of markdown skills and artifact templates** that make the AI-native software development lifecycle explicit, auditable, and repeatable.

## The idea

In the traditional SDLC, every stage is a human gate: product managers write requirements, architects write designs, engineers write code, QA verifies, release teams ship, and operations watches production. When AI agents can write code in hours, that linear, document-and-handoff model becomes the bottleneck.

The AI-native SDLC reimagines the lifecycle as a loop where **each stage commits an artifact the next stage can read**:

```
idea → intent.md → spec.md → plan.md → diff + tests → review → deploy → monitor
     ↑                                                             ↓
     └─────────────── close the loop ──────────────────────────────┘
```

The artifact chain is the audit trail: who asked for what, what the agent produced, and who approved it. Humans stay accountable for judgment; agents handle the mechanical work in between. (Claude, 2026)

This repo gives your team the skills and templates to run that loop.

## What is in this package

- **12 skills** covering all six stages of the AI-Native SDLC:
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
- **MCP client templates**: pre-wired for GitHub, Jira, Slack, and Monday.
- **Install and validation tooling**: `scripts/install.sh`, `scripts/validate.py`, `Makefile`, and a GitHub Actions workflow.

## How a team should manage the AI-DLC with this repo

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

Slack, Jira, GitHub, and Monday are not replaced; they are connected. Use the provided MCP client templates to let the agent read tickets, post updates, create issues, and query boards under the same human approval gates. The templates point to the official remote MCP endpoints; you only need to provide your tokens.

### 6. Regression-test your agent configuration

`CLAUDE.md`, skills, hooks, and MCP setup steer the agent. They deserve the same regression testing as code. Use the `04-continuous-evals` skill to build an eval suite and run it in CI whenever configuration changes.

## Quick start

1. **Install the skills** for your client:

   ```bash
   make install INSTALL_CLIENT=claude    # or codex, agents, github
   ```

2. **Configure MCP** by copying the right template and adding your credentials:

   ```bash
   # Claude Code
   cp mcp/claude-mcp.json ~/.claude/.mcp.json

   # OpenAI Codex
   cp mcp/mcp.json ~/.codex/.mcp.json

   # GitHub Copilot / VS Code
   cp mcp/copilot-mcp.json .vscode/mcp.json
   ```

   Then set the environment variables or config values for `GITHUB_TOKEN`, `ATLASSIAN_TOKEN`, `SLACK_TOKEN`, and `MONDAY_TOKEN`.

3. **Use a skill** in your agent:

   - **Claude Code**: `/01-intent-capture`
   - **OpenAI Codex**: `$01-intent-capture`
   - **GitHub Copilot / cloud agent**: refer to the `AGENTS.md` and `.github/copilot-instructions.md` in the repo

4. **Validate and test** before committing changes:

   ```bash
   make
   ```

## Repository layout

```
.
├── skills/                 # canonical skill source
├── templates/              # SDLC artifact templates
├── mcp/                    # MCP client templates
├── scripts/                # install.sh and validate.py
├── tests/                  # pytest validation
├── .github/workflows/      # CI
├── AGENTS.md               # cross-client agent onboarding
├── CLAUDE.md               # Claude Code project context
└── .github/copilot-instructions.md
```

## License

Apache-2.0. See [LICENSE](LICENSE).

## Reference

Claude. (2026, August 21). *The AI-Native SDLC Playbook*. https://claude.com/blog/the-ai-native-sdlc-playbook