---
name: 04-continuous-evals
description: Define and run evaluation prompts that test whether agent configuration still produces acceptable changes. Use when CLAUDE.md, skills, or hooks change.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Edit
  - Bash(git status:*)
  - Bash(git diff:*)
  - Bash(git log:*)
  - Bash(git add:*)
  - Bash(git commit:*)
  - Bash(git switch:*)
  - Bash(bash:*)
  - Bash(claude -p:*)
metadata:
  stage: "04-test"
  persona: "qa, tech-lead, platform, security"
  requires: "03-claude-md, 04-feedback-loop"
  produces: "evals/"
  indicators: "eval-pass-rate, regressions-caught-in-ci"
  mcp: "github, playwright"
  maturity: "stable"
---

# Continuous evals

## Job

Regression-test the agent's configuration the way you would test code.

## Who uses this

- **QA / Test engineers** who want to catch regressions in agent behavior.
- **Platform engineers** changing `CLAUDE.md` or skills.
- **SREs** adding an eval for a new incident class.

## Example prompts

- "Create an eval suite for this repo's agent configuration."
- "A bug where CSV export failed on empty reports made it to production. Add an eval."
- "Run the eval suite and report the pass rate."

## Steps

1. Collect 5–20 real tasks with accepted/expected outcomes.
2. For each task, create an eval file under `evals/` with:
   - `prompt`: what the agent is asked to do
   - `check.sh`: the deterministic assertions
3. Provide a CI workflow that runs evals on changes to `CLAUDE.md` or `skills/`.
4. Add an eval for every production incident once the fix ships.
5. Gate merges on the pass rate.

## Output

- `evals/*.json` and `evals/*.sh` files.
- A CI gate and a pass-rate report.

## Measure

| Indicator | Type | Where it comes from |
|---|---|---|
| `eval-pass-rate` | leading | an external system |
| `regressions-caught-in-ci` | lagging | an external system |

Neither is computable from this repository — read them from your eval run history and CI. `templates/metrics.md` has a place to record both.

See `references/metrics-catalog.md` for the full indicator set.
