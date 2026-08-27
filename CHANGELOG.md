# Changelog

## 0.4.0 (unreleased)

### Added

- **The integration branch.** `05-integration` and
  `references/integration-branch.md` cover how several intents converge and reach
  production: intents merge to `integration`, the combination is validated as a
  set, promotion to `main` is human-only, and each intent then ramps
  independently behind its own feature flag. Merge and release are separate
  events, so intents promote together and still fail apart. The rationale and its
  sources are documented, including when *not* to run an integration branch —
  `integration-failure-rate` near zero for a quarter is the retirement signal.
- `ai-dlc backlog --collisions` — reports in-flight intents whose plans claim the
  same files, using the `## Files that change` contract. Collisions are cheap to
  fix before either intent branches and expensive to fix in the merge queue.
- Four integration indicators: `merge-queue-depth`, `deploy-lag`,
  `integration-failure-rate`, and `flag-ramp-duration`.
- `templates/workflows/ai-dlc-integration.yml`, which validates the combination
  rather than repeating per-PR CI, and deliberately does not automate promotion.

### Changed

- `templates/05-deploy.md` is now a promotion and flag-ramp record — what it
  promoted with, the flag and its expiry, the ramp table, the rollback mechanism,
  and deploy lag — rather than a release document.
- `validate` now checks that documented CLI **flags** exist, not just
  subcommands. Same defect class, caught at the same point.

### Fixed

- **No skill produced `06-lessons.md`.** It was in the chain, the templates, and
  the completeness metric, but nothing authored it, so a perfectly executed
  intent capped at 4/6 and the flagship indicator read broken. `06-closing-the-loop`
  now writes it, and `05-integration` writes `05-deploy.md`.

## 0.3.0

### Added

- Six skills for plays the package did not cover: `03-subagents`,
  `03-parallel-sessions`, `03-org-skills`, `05-managed-settings`,
  `05-cicd-integration`, and `platform-metrics`. Cross-cutting plays use the
  `platform-` prefix rather than a number: the playbook has six stages, and a
  `07-` prefix would imply a seventh.
- `ai-dlc metrics` — computes eight delivery indicators from the `intents/` tree
  and local git history, with `--json`, `--markdown`, and `--fail-under-*`
  thresholds for CI.
- `ai-dlc backlog` — reads `intents/` as a work queue, including intents that
  exist only on unmerged branches. Previously documented but not implemented.
- `ai-dlc adoption` — derives the play dependency graph and rollout waves from
  skill metadata.
- `ai-dlc migrate` — moves a project from the old flat `intent/ spec/ plan/`
  layout to `intents/<id>/`. Dry run by default, `git mv` where possible.
- `references/indicators.yaml` — machine-readable catalog of every indicator the
  playbook names, plus `metrics-catalog.md`, `adoption.md`, `observability.md`,
  and `roles.md`.
- Templates for subagents (`verifier`, `simplifier`, `researcher`,
  `spec-auditor`), GitHub Actions workflows, and org policy skills.
- `04-review.md`, `05-deploy.md`, `06-lessons.md`, `metrics.md`, and `AGENTS.md`
  templates, completing the artifact chain.
- `governance/managed-settings.json` with sandboxing and a network allowlist;
  `no-self-approve.sh` and `detect-bands.sh` hooks; a local audit log at
  `.ai-dlc/audit.jsonl`.
- `ai_dlc/yamlite.py`, a strict YAML-subset parser that doubles as the
  cross-client frontmatter portability guard.

### Changed

- **Skill frontmatter** now carries `allowed-tools` and a `metadata` block with
  stage, persona, dependencies, produced artifacts, indicators, and MCP servers.
  Top-level keys are restricted to the Agent Skills schema; custom data nests
  under `metadata` as strings.
- **The package has no runtime dependencies.** PyYAML moved to the dev extra,
  where it is used as a differential check against `yamlite`.
- `ai-dlc` subcommands dispatch to importable modules instead of shelling out to
  scripts, so they inherit the caller's environment and are unit-testable.
- `mcp-sync` emits `codex-mcp.toml`, and the Claude and Copilot wrapper keys are
  now correct — `claude-mcp.json` uses `mcpServers`, `copilot-mcp.json` uses
  `servers`. They were swapped.
- MCP fragment types corrected from `remote`/`command` to `http`/`sse`/`stdio`.
- `init-repo` scaffolds `intents/<id>/`, subagents, and optional CI workflows,
  and no longer creates the flat `intent/ spec/ plan/` directories.
- Artifact templates renamed to `01-intent.md`, `02-spec.md`, `03-plan.md`.
  `ai-dlc migrate` renames a vendored `templates/` directory in place and adds
  the templates the chain gained, without overwriting customized copies.
- `validate` rebuilt: collects all problems instead of short-circuiting, and adds
  checks for the dependency graph, indicator registry drift, MCP fragment shape
  and placeholders, generated-config drift, hook executability in the git index,
  literal secrets, the example artifact chain, and documented-but-missing CLI
  subcommands.
- Tests import from `ai_dlc.validate` rather than reimplementing its rules.

### Fixed

- `intent-survival`'s approximation caveat now appears in the rendered report
  and the Markdown output, not only in the skill documentation. A team that
  squash-merges reads 0% while shipping normally, and the report says so.

- **Hooks read stdin twice**, so the second read was always empty and
  `block-test-edit.sh` and `migration-ticket.sh` never actually gated anything.
  All hooks now read the payload once through `_lib.sh`.
- `ai-dlc install` passed a subprocess environment with no `PATH` or `HOME`.
- `init-repo` deleted the user's existing `.claude/skills/` before copying.
- `validate` skipped every MCP check whenever a skill failed.
- `backlog` and `metrics` could not see intents that live only on branches.
- Git timestamps ending in `Z` failed to parse before Python 3.11.
- `examples/github-centric-team.md` documented `ai-dlc backlog`, which did not
  exist.

## 0.2.0

- CLI, governance hooks, `init-repo`, example evals, `pyproject.toml`,
  `CONTRIBUTING.md`, templates, and the release workflow.

## 0.1.0

- 13 skills, 17 MCP configs, templates, examples, README.
