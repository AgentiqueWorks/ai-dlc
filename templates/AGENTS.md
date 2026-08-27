# <Project name>

Cross-client agent instructions. Claude Code reads `CLAUDE.md`; Codex and other
Agent Skills clients read this file. Keep the two in sync.

## Commands

- **Build:** <command>
- **Test:** <command>
- **Lint:** <command>

## The loop

Work enters as an intent and moves through a committed artifact chain:

```
intents/<id>/01-intent.md -> 02-spec.md -> 03-plan.md -> code + tests
          -> 04-review.md -> 05-deploy.md -> 06-lessons.md
```

One branch per intent (`intent/<id>`), one PR, a human merges.

## Conventions

- <convention 1>
- <convention 2>

## Guardrails

- Never edit a test to make it pass; fix the code.
- Never approve your own change.
- Deterministic gates live in `.claude/hooks/` and CI, not in the prompt.

## Things agents get wrong here

- <common mistake 1>
- <common mistake 2>
