---
name: 04-continuous-evals
description: Define and run evaluation prompts that test whether agent configuration still produces acceptable changes. Use when CLAUDE.md, skills, or hooks change.
---

# Continuous evals

## Job

Regression-test the agent's configuration the way you would test code.

## Steps

1. Collect 20–50 real tasks with their accepted/expected outcomes.
2. For each task, write an eval file under `evals/` containing a prompt and a `check.sh` that asserts the outcome.
3. Provide a CI workflow that runs these evals whenever `CLAUDE.md` or `.claude/**` changes.
4. Add an eval for each production incident once the fix ships.
5. Report the pass rate and fail any change that drops it below the configured threshold.

## Output

- `evals/*.json` and `evals/check.sh`.
- A CI workflow that gates configuration changes on eval pass rate.