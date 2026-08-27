---
name: 05-cicd-triage
description: Diagnose failed CI builds and flaky tests in the pipeline, producing short actionable summaries. Use inside a CI/CD job or after a failed run.
---

# CI/CD triage

## Job

Run Claude as a non-interactive triage step in the pipeline.

## Who uses this

- **Platform engineers** who want failing builds triaged automatically.
- **SREs** investigating a flaky test.
- **Engineers** who need a quick summary before they dig in.

## Example prompts

- "The build failed. Read the log and tell me if it is flaky or real."
- "Summarize the three most likely root causes from `out/build.log`."
- "Draft a triage note for the PR thread."

## Steps

1. Read the build, test, or lint output.
2. If a CI platform MCP is configured (GitHub, GitLab, Vercel), fetch the run log with `get_workflow_run` or `get_deployment`.
3. Determine whether the failure looks flaky or real.
4. Identify the most likely root cause.
5. Write a three-line summary for the PR thread or a `triage.md` artifact.
6. If safe and approved, suggest or apply a fix; otherwise escalate to a human.

## Output

- A concise `triage.md` or PR comment.
- A recommendation: fix, retry, or escalate.