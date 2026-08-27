---
name: 05-cicd-integration
description: Run agents inside CI/CD with claude -p and claude-code-action for PR review, failure triage, and eval gating, under the same permissions and approval gates as an interactive session. Use once the PR review loop and hooks are established.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Edit
  - Bash(git status:*)
  - Bash(git add:*)
  - Bash(git commit:*)
  - Bash(gh workflow:*)
  - Bash(gh run view:*)
  - Bash(gh pr create:*)
metadata:
  stage: "05-deploy"
  persona: "platform, engineer, tech-lead"
  requires: "05-pr-review, 05-release-gate"
  produces: ".github/workflows/"
  indicators: "ci-first-pass-rate, pr-review-time"
  mcp: "github, gitlab"
  maturity: "beta"
---

# CI/CD integration

## Job

Move the plays that should run every time — review, triage, eval gating — out of
somebody's terminal and into the pipeline, without loosening the gates that apply
interactively.

## Who uses this

- **Platform engineers** wiring agents into the pipeline.
- **Engineers** who want triage on a red build without asking for it.
- **Tech leads** gating merges on the eval suite.

## Prerequisites

This play comes late on purpose. Automate a review loop before it is good and you
will automate the noise. Before starting:

- `05-pr-review` produces findings people act on.
- `05-release-gate` hooks block what they should.
- `04-continuous-evals` has a suite worth gating on.

## Example prompts

- "Add a PR review workflow that posts findings but does not approve."
- "Wire CI triage so a failed test run gets a three-line diagnosis."
- "Gate merges on the eval suite when CLAUDE.md or a skill changes."

## Steps

1. **Start from the templates.** `templates/workflows/` has four working
   starting points: `claude-pr-review.yml`, `claude-cicd-triage.yml`,
   `ai-dlc-evals.yml`, and `ai-dlc-validate.yml`. Copy, do not invent.
   `references/workflow-recipes.md` explains what each one assumes.
2. **Use `claude -p` for non-interactive work.** One prompt, a scoped
   `--allowed-tools`, and an exit code. For hosted PR review, `claude-code-action`
   handles checkout, comments, and check runs for you.
3. **Scope tools per job, not per repo.** Triage is read-only:
   `Read, Grep, Glob, Bash(gh run view:*)`. Review adds the ability to comment.
   Neither gets `Write` to source.
4. **Keep separation of duties in CI.** A workflow must never approve or merge.
   Findings are advisory; branch protection and a human code owner are the gate.
   The `no-self-approve.sh` hook enforces this locally; branch protection enforces
   it in the forge.
5. **Give the job the least token it can work with.** A read-only triage job does
   not need write scopes. Set `permissions:` per job explicitly rather than
   inheriting the workflow default.
6. **Fetch full history where it matters.** `actions/checkout` defaults to
   `fetch-depth: 1`; `ai-dlc metrics` and any diff-against-base logic need
   `fetch-depth: 0` or they return confidently wrong numbers.
7. **Gate on the eval pass rate, not on every eval.** A suite required to be 100%
   green gets weakened until it means nothing. Set a threshold, publish the trend.
8. **Publish results where they are read** — the step summary, a PR comment, the
   check run. A finding in a log nobody opens is not a finding.
9. **Budget it.** Agent jobs cost per run. Trigger on the paths that matter
   (`CLAUDE.md`, `.claude/**`, `evals/**`) rather than on every push, and skip
   draft PRs.

## Failure modes

- **Review on every push.** Noise, cost, and a team that stops reading comments.
  Trigger on `ready_for_review` and `synchronize`, and skip drafts.
- **A workflow with write access to source.** The pipeline becomes an
  unreviewable committer. Keep agent jobs read-only plus comment.
- **Triage that is always confident.** Require it to say "cause not determined"
  when it is not, or people will stop trusting the ones that are right.

## Output

- Workflows under `.github/workflows/` for review, triage, evals, and validation.
- Per-job `permissions:` blocks and per-job tool allowlists.
- Branch protection requiring a human code-owner approval.
- Results posted to the PR and the step summary.

## Measure

| Indicator | Type | Where it comes from |
|---|---|---|
| `ci-first-pass-rate` | leading | an external system |
| `pr-review-time` | lagging | an external system |

`pr-review-time` should fall once mechanical findings are caught before a human
opens the PR. If it does not, the review is adding a queue rather than removing
work.

See `references/metrics-catalog.md` for the full indicator set.
