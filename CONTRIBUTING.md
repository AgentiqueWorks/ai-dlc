# Contributing

## The shape of a change

This is a markdown-first package: prefer a new `SKILL.md`, template, or reference
over new code. The exception is `ai_dlc/`, which is the deterministic tooling
layer — validation, scaffolding, measurement. Those things must be exact and
testable, so they are code, and every one of them ships with tests.

## Before you open a pull request

```bash
make validate
make test
```

Both must pass with zero errors and zero warnings. `make validate` also checks
things that are easy to get wrong by hand:

- Frontmatter stays inside the portable YAML subset.
- The play dependency graph has no cycles and no dangling references.
- Every indicator a skill names exists in `references/indicators.yaml`.
- Every MCP server a skill names has a config fragment.
- The generated MCP configs match `mcp/configs/`.
- Hooks are executable **in the git index**, not just on your machine.
- Every `ai-dlc <command>` mentioned in the docs is a real subcommand.
- No literal credentials anywhere in the tree.

## Adding a skill

1. Create `skills/<stage>-<name>/SKILL.md`. Prefixes `00`–`06` map to the six
   stages; `07` is for cross-cutting plays.
2. Frontmatter: `name` (must equal the directory), `description` (say when to use
   it), `allowed-tools` (least privilege), and a full `metadata` block —
   `stage`, `persona`, `requires`, `produces`, `indicators`, `mcp`, `maturity`.
3. Body: `## Job`, `## Steps`, `## Output` are required. Add `## Measure` naming
   the indicators the play moves.
4. Anything long goes in the skill's own `references/`, cited from the body. An
   uncited reference file is a warning.
5. New skills ship as `maturity: beta`.

## Adding an indicator

Add it to `references/indicators.yaml` first. If it is not `external`, implement
it in `ai_dlc/metrics.py` and register it — validation fails if the catalog and
the registry disagree, in either direction. Be honest about `approximate` and
about what makes an indicator `conditional`.

## Adding a hook

Source `_lib.sh` and use `read_payload`. Hooks are deterministic gates: if the
decision needs judgement, it is not a hook. Keep them fast — anything slow enough
to notice will be routed around.

## Release

Bump `ai_dlc/__init__.py`, `pyproject.toml`, and `.claude-plugin/plugin.json`,
update `CHANGELOG.md`, then tag `vX.Y.Z`.
