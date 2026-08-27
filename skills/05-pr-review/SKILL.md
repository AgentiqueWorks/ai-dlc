---
name: 05-pr-review
description: Run a multi-pass AI review on a pull request against the organization's REVIEW.md, intent.md, spec.md, and plan.md. Use at the Deploy stage.
---

# PR review

## Job

Review a PR with consistent, policy-driven passes before a human code owner approves.

## Steps

1. Load the PR diff, `REVIEW.md`, `spec.md`, and `plan.md`.
2. Run the defined passes: bugs, security, compliance with spec and plan.
3. Tag each finding with the pass and severity (Important vs Nit).
4. Cap the number of nits reported and summarize the rest.
5. Exclude generated files and anything CI already enforces.
6. If requested, respond to review comments and push fixes, but never approve the PR (that is for a human).

## Output

- A structured review with tagged, severity-ranked findings.
- A recommendation on whether the change matches the accepted intent and plan.