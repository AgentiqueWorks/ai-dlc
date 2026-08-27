---
name: 05-pr-review
description: Run a multi-pass AI review on a pull request against the organization REVIEW.md, intent.md, spec.md, and plan.md. Use at the Deploy stage.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Edit
  - Bash(git diff:*)
  - Bash(git log:*)
  - Bash(gh pr view:*)
  - Bash(gh pr create:*)
  - Bash(gh pr comment:*)
  - Agent
metadata:
  stage: "05-deploy"
  persona: "tech-lead, code-owner, engineer, security"
  requires: "03-plan-mode, 03-claude-md"
  produces: "intents/<id>/04-review.md"
  indicators: "pr-review-time, plan-diff-alignment, rework-after-review, policy-cite-findings"
  mcp: "github, gitlab"
  maturity: "stable"
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

1. Load the PR diff, `REVIEW.md`, `intents/<id>/02-spec.md`, `intents/<id>/03-plan.md`, and `CLAUDE.md`.
2. If the PR is on GitHub or GitLab, use the `github` or `gitlab` MCP to fetch the diff and comments.
3. Run the passes defined in `REVIEW.md`:
   - bugs / logic errors
   - security / vulnerabilities
   - compliance with `02-spec.md` and `03-plan.md`
4. Tag each finding with the pass and severity.
5. Cap the number of nits; summarize the rest.
6. Exclude generated files and anything CI already enforces.
7. If fixing comments, address them and push the changes, but do not approve the PR.

## Output

- `intents/<id>/04-review.md` with a structured review.
- A recommendation on whether the change matches the accepted intent and plan.
- Updated code if asked to address comments.

## Measure

| Indicator | Type | Where it comes from |
|---|---|---|
| `plan-diff-alignment` | lagging | `ai-dlc metrics` |
| `rework-after-review` | lagging | `ai-dlc metrics` |

`policy-cite-findings` should fall toward zero: a policy the review keeps citing belongs in an org skill so the agent applies it during Build instead.

See `references/metrics-catalog.md` for the full indicator set.
