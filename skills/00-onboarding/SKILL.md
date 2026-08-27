---
name: 00-onboarding
description: Help a new user or team pick the right first skill and understand the AI-Native SDLC artifact chain. Use on day one or when introducing the system.
---

# Onboarding

## Job

Orient a team member and point them to the right first skill.

## When to use this

- A new engineer, PM, designer, QA, SRE, or security lead opens this repo for the first time.
- A team is adopting the AI-Native SDLC and does not know where to start.

## Steps

1. Ask the user's role: PM, designer, engineer, QA, SRE, security, or platform.
2. Ask the context: startup (few gates, one repo) or enterprise (policy, compliance, multiple systems).
3. Recommend the first skill and the first artifact:
   - **PM** → `01-intent-capture` → `intents/<id>/01-intent.md`
   - **Designer** → `02-spec-writer` → `intents/<id>/02-spec.md` (with Figma)
   - **Engineer** → `03-plan-mode` → `intents/<id>/03-plan.md`
   - **QA** → `04-continuous-evals` → `evals/`
   - **Tech lead** → `05-pr-review` → `intents/<id>/04-review.md`
   - **SRE** → `06-closing-the-loop` → `intents/<id>/01-intent.md` or `bands.yaml`
   - **Security** → `06-security-scan` → `intents/<id>/01-intent.md` or PR
4. For a GitHub-centric team, explain one branch per intent: `intent/<id>` with `intents/<id>/01-intent.md`, `02-spec.md`, `03-plan.md`, `04-review.md`, `05-deploy.md`, `06-lessons.md`.
5. Show the install command for their client: `make install INSTALL_CLIENT=claude` (or codex, agents, github).
6. Show how to configure MCP by copying the right `mcp/*.json` template.
7. Summarize the artifact chain: `01-intent.md` → `02-spec.md` → `03-plan.md` → diff + tests → `04-review.md` → `06-lessons.md`.

## Output

- A one-paragraph recommendation for the user's role.
- The exact command to run their first skill.
- A link to `references/team-flows.md` and `examples/github-centric-team.md` for detailed examples.