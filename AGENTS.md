# AI-Native SDLC Skills — Agent Onboarding

You are an AI agent operating inside the `ai-native-sdlc-skills` repository.

## Conventions

- Skills live under `skills/<stage>-<name>/SKILL.md`.
- Each skill is an Agent Skills bundle: a `SKILL.md` with YAML frontmatter (`name`, `description`, etc.) and markdown instructions.
- The canonical skill tree is `skills/`. Installation scripts copy or symlink it into client-specific folders (`~/.claude/skills/`, `~/.codex/skills/`, `.agents/skills/`, `.github/skills/`).
- Use the artifact templates in `templates/` when the skill asks you to produce a document.
- MCP server settings are in `mcp/`. Read the user’s actual local MCP config rather than the templates when executing real calls.

## Commands

- `make validate` — check every `SKILL.md` for frontmatter and schema correctness.
- `make test` — run the test suite.
- `make install` — install skills for the client chosen in `INSTALL_CLIENT` (default: `claude`).

## What not to do

- Do not commit secrets or OAuth tokens.
- Do not rewrite `SKILL.md` frontmatter to use client-specific keys unless the client you are writing for explicitly requires them.
- Do not skip the `name`/`description` validation for new skills.