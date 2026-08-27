# Workflow recipes

What each template in `templates/workflows/` assumes, and where it will bite you.

## `claude-pr-review.yml` — first-pass review

**Assumes:** a `REVIEW.md` at the repository root, an `ANTHROPIC_API_KEY` secret,
and branch protection requiring a human approval.

**Permissions:** `contents: read`, `pull-requests: write`. Never `contents: write`
— a review job that can push is not a review job.

**Watch for:** running on every `synchronize` turns a busy PR into twenty
reviews. Skip drafts, and consider only re-reviewing when the diff has grown by
more than a trivial amount.

## `claude-cicd-triage.yml` — failure triage

**Assumes:** a `workflow_run` trigger on the workflow whose failures you care
about, and `actions: read` to fetch logs.

**Tools:** read-only plus `gh run view` and `gh pr comment`. It diagnoses; it does
not fix. A triage job that opens fix PRs will open them for flaky tests.

**Watch for:** `workflow_run` fires on the default branch context, so the
comment target has to be resolved from the run's head branch, not from
`github.ref`.

## `ai-dlc-evals.yml` — configuration regression tests

**Assumes:** `evals/*.json` with a `prompt` and an executable `check` script, and
that the checks are deterministic.

**Triggers on the configuration paths only** — `CLAUDE.md`, `.claude/skills/**`,
`.claude/hooks/**`, `.mcp.json`, `evals/**`. Running the suite on every code push
is expensive and tells you nothing new.

**Watch for:** gate on a pass-rate threshold, not on every eval. A required-green
suite gets weakened one exemption at a time until it certifies nothing.

## `ai-dlc-validate.yml` — artifact chain and structure

**Assumes:** `pip install ai-dlc` and `fetch-depth: 0`.

Cheap, deterministic, no model calls. Run it on every PR. It catches a broken
artifact chain, a stale MCP config, a hook that lost its executable bit, and a
documented CLI subcommand that does not exist.

## `ai-dlc-bands.yml` — closing the loop

**Assumes:** `detect-bands.sh` is wired to your real metrics store, and
`bands.yaml` declares tiers and a confidence gate.

The detector decides; the agent only runs when the detector says a 3-sigma band
broke. That ordering is the whole design — never let the model decide whether it
should have been invoked.

**Watch for:** a cron this frequent needs a cooldown, or one bad deploy produces
a new intent every fifteen minutes.

## Rules that apply to all of them

1. Set `permissions:` per job. The workflow default is too broad for an agent.
2. `fetch-depth: 0` whenever anything reads history.
3. Pin actions to a major version at minimum; a floating action in a job that can
   comment on PRs is a supply-chain decision.
4. Put the API key in secrets, never in `env:` at workflow level where every job
   inherits it.
5. Have the job fail loudly when the agent produced nothing. A silent no-op reads
   as a pass.
