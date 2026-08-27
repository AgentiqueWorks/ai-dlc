# AI-Native SDLC Skills — cross-client agent instructions

Claude Code reads `CLAUDE.md`. Codex, Copilot, and other Agent Skills clients
read this file. The two are kept in sync deliberately; change both.

## Commands

- `make validate` — validate skills, MCP configs, hooks, templates, and docs.
- `make test` — run `pytest tests/`.
- `make install INSTALL_CLIENT=codex` — install skills for a specific client.

## Conventions

- Skills live at `skills/<stage>-<name>/SKILL.md`. The `name` in the frontmatter
  must equal the parent directory name.
- Frontmatter top-level keys are a closed set: `name`, `description`,
  `allowed-tools`, `metadata`, `license`, `version`. Anything else belongs under
  `metadata`, as a string.
- Frontmatter must stay inside the portable YAML subset: no anchors, aliases,
  merge keys, block scalars, flow collections, or tabs. Clients that do not use a
  full YAML parser have to be able to read it. `tests/test_yamlite.py` enforces
  this.
- `allowed-tools` is honoured by Claude Code and ignored by Codex and Copilot.
  Write it for least privilege, but never rely on it as the only control — the
  real gates are hooks and settings.
- Artifacts are `intents/<id>/NN-name.md`, one branch per intent.

## Rules

- Do not commit secrets. MCP credentials are `${VAR}` placeholders; validation
  scans for literal tokens and fails on them.
- Do not rewrite frontmatter into client-specific keys.
- Do not delete a skill's `references/` or `assets/` directories when copying.
- Do not edit generated files: `mcp/mcp.json`, `mcp/claude-mcp.json`,
  `mcp/copilot-mcp.json`, `mcp/codex-mcp.toml`. Run `make mcp-sync`.
- Never edit a test to make it pass. Fix the code.
- Never approve your own change.
