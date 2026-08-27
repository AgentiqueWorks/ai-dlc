---
name: 04-continuous-evals
description: Define and run evaluation prompts that test whether agent configuration still produces acceptable changes. Use when CLAUDE.md, skills, or hooks change.
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