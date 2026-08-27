---
name: 05-cicd-triage
description: Diagnose failed CI builds and flaky tests in the pipeline, producing short actionable summaries. Use inside a CI/CD job or after a failed run.
---

# CI/CD triage

## Job

Run Claude as a non-interactive triage step in the pipeline.

## Steps

1. Read the build, test, or lint output.
2. Determine whether the failure looks flaky or real.
3. Identify the most likely root cause.
4. Write a three-line summary for the PR thread or a `triage.md` artifact.
5. If safe and approved, suggest or apply a fix; otherwise hand off to a human.

## Output

- A concise `triage.md` or PR comment.
- A recommendation: fix, retry, escalate.