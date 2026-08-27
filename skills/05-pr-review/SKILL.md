---
name: 05-pr-review
description: Run a multi-pass AI review on a pull request against the organization REVIEW.md, intent.md, spec.md, and plan.md. Use at the Deploy stage.
---

# PR review

## Job

Review a PR with consistent, policy-driven passes before a human code owner approves.

## Who uses this

- **Tech leads** running a first-pass review.
- **Security engineers** verifying policy compliance.
- **Authors** asking the agent to address review comments.

## Example prompts

- "Review this PR against `REVIEW.md`, `spec.md`, and `plan.md`."
- "Tag each finding as Bug, Security, or Compliance and rank it Important or Nit."
- "Fix the review comments I just added and push the changes."

## Steps

1. Load the PR diff, `REVIEW.md`, `spec.md`, `plan.md`, and `CLAUDE.md`.
2. If the PR is on GitHub or GitLab, use the `github` or `gitlab` MCP to fetch the diff and comments.
3. Run the passes defined in `REVIEW.md`:
   - bugs / logic errors
   - security / vulnerabilities
   - compliance with `spec.md` and `plan.md`
4. Tag each finding with the pass and severity.
5. Cap the number of nits; summarize the rest.
6. Exclude generated files and anything CI already enforces.
7. If fixing comments, address them and push the changes, but do not approve the PR.

## Output

- A structured review with tagged, severity-ranked findings.
- A recommendation on whether the change matches the accepted intent and plan.
- Updated code if asked to address comments.