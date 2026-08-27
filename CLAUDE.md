# AI-Native SDLC Skills

## Commands

- `make validate` — validate skills, MCP configs, hooks, templates, examples, and docs.
- `make test` — run `pytest tests/`.
- `make install` — install skills into `~/.claude/skills` by default.
- `make mcp-sync` — regenerate the combined MCP configs after editing `mcp/configs/`.

## Architecture

- `ai_dlc/` holds every module; `scripts/*.py` are three-line wrappers so the repo
  runs from a fresh clone without `pip install`. Put logic in `ai_dlc/`, never in
  `scripts/`.
- **The package has no runtime dependencies.** `ai_dlc/yamlite.py` is a strict
  YAML-subset parser that replaces PyYAML. Do not add a runtime dependency
  without a very good reason; PyYAML is a dev extra used only as a differential
  check in `tests/test_yamlite.py`.
- Code must run on the declared floor (Python 3.10). Use
  `from __future__ import annotations` in every module.

## Conventions

- Skills are `skills/<stage>-<name>/SKILL.md`. `platform-` is the cross-cutting prefix for plays that are not a stage.
- Frontmatter top-level keys are a **closed set**: `name`, `description`,
  `allowed-tools`, `metadata`, `license`, `version`. Everything custom nests
  under `metadata` as **strings** — the Skills API metadata contract is
  string-valued, and arbitrary top-level keys are rejected by strict loaders.
- The play dependency graph lives in `metadata.requires` and nowhere else.
  `unlocks` is derived, never stored.
- `references/indicators.yaml` is the single source of truth for indicators.
  `ai_dlc/metrics.REGISTRY` must match it exactly; validation enforces this.
- Artifacts are `intents/<id>/NN-name.md`. `## Files that change` in `03-plan.md`
  is a parse contract that `plan-diff-alignment` depends on.
- MCP fragments are one server per file, filename matching the server key, with
  `${VAR}` placeholders for every credential.

## Things Claude gets wrong

- Do not overwrite the user's real `~/.claude/.mcp.json` without a prompt.
- Do not remove a skill's `references/` or `assets/` directories when copying.
- Do not change a `SKILL.md` `name` to anything other than the parent directory.
- Do not `rmtree` a target skills directory during install or scaffold — users
  keep their own skills there. Replace only the directories this package owns.
- Do not read stdin twice in a hook. The second read is empty and the gate
  silently stops working. Use `read_payload` from `governance/hooks/_lib.sh`.
- Do not assume `intents/` is on disk. Under one-branch-per-intent, the backlog
  usually lives on unmerged branches; read it through `repo.load_intents`.
- Do not use `datetime.fromisoformat` on a git timestamp directly. It rejects a
  trailing `Z` before Python 3.11. Use `gitio._parse_iso`.
- Do not report a history-derived metric from a shallow clone. Suppress it.
- Do not hand-edit `mcp/mcp.json`, `claude-mcp.json`, `copilot-mcp.json`, or
  `codex-mcp.toml`. They are generated, and validation fails on drift.
