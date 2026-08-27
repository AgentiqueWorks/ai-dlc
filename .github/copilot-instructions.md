# AI-Native SDLC — Copilot instructions

This repository implements the AI-Native SDLC playbook as Agent Skills. Skills
live in `.github/skills/` (run `ai-dlc install github`) and in the canonical
`skills/` tree.

## The loop

Work enters as an intent and moves through a committed artifact chain, one folder
and one branch per intent:

```
intents/<id>/01-intent.md -> 02-spec.md -> 03-plan.md -> code + tests
          -> 04-review.md -> 05-deploy.md -> 06-lessons.md
```

Branch `intent/<id>`, one pull request, a human merges.

## Commands

- `make validate` — validate skills, MCP configs, hooks, templates, and docs.
- `make test` — run the test suite.
- `ai-dlc backlog` — see what is in flight.
- `ai-dlc metrics` — see whether the loop is getting faster.

## MCP

Copy `mcp/copilot-mcp.json` into your VS Code MCP configuration. It uses the
`servers` wrapper key that VS Code expects. Credentials are `${VAR}`
placeholders; supply them from your environment.

## Rules

- Never edit a test to make it pass. Fix the code.
- Never approve or merge your own change.
- Do not commit secrets; validation scans for literal tokens.
- Do not edit generated files under `mcp/` — run `make mcp-sync`.
- Keep `## Files that change` in `03-plan.md` accurate: it is a parse contract
  that `plan-diff-alignment` depends on.
