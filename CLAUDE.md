# AI-Native SDLC Skills

## Commands

- `make validate` — validate all `SKILL.md` files.
- `make test` — run `tests/test_skills.py`.
- `make install` — install skills into `~/.claude/skills` by default.

## Conventions

- Skills are in `skills/<stage>-<name>/SKILL.md`.
- Every `SKILL.md` must have `name` and `description` in YAML frontmatter.
- The install script in `scripts/install.sh` copies the canonical `skills/` tree to `~/.claude/skills/`, `~/.codex/skills/`, `.agents/skills/`, or `.github/skills/`.
- MCP configs live in `mcp/`. They are templates; real credentials come from the user’s environment or local config.

## Things Claude gets wrong

- Do not overwrite the user’s real `~/.claude/.mcp.json` without a prompt.
- Do not remove a skill’s `references/` or `assets/` directories when copying.
- Do not change the `name` field of a `SKILL.md` to anything other than the parent directory name.