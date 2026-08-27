---
name: 05-integration
description: Converge several intents on an integration branch, validate them as a combination, promote to production under human authorization, and ramp each intent independently behind its own feature flag. Use when more than one intent lands per day.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Edit
  - Bash(git status:*)
  - Bash(git log:*)
  - Bash(git diff:*)
  - Bash(git switch:*)
  - Bash(git merge:*)
  - Bash(git add:*)
  - Bash(git commit:*)
  - Bash(gh pr view:*)
  - Bash(gh pr list:*)
  - Bash(gh run view:*)
  - Bash(ai-dlc:*)
metadata:
  stage: "05-deploy"
  persona: "release-manager, platform, tech-lead, engineer"
  requires: "05-pr-review, 05-release-gate"
  produces: "intents/<id>/05-deploy.md"
  indicators: "merge-queue-depth, deploy-lag, integration-failure-rate, flag-ramp-duration"
  mcp: "github, gitlab, vercel, datadog"
  maturity: "beta"
---

# Integration and promotion

## Job

Get several independently developed intents into production without batching
them into a release, and without discovering their interactions in production.

Per-PR CI answers *does this intent work against `main` as it was when the branch
was cut?* It cannot answer *do the six intents landing today work together?* This
play answers the second question, then ships each intent on its own schedule.

## Who uses this

- **Release managers** who authorize promotion and hold the approval token.
- **Platform engineers** who own the queue and its health signals.
- **Tech leads** deciding whether the integration branch is earning its cost.
- **Engineers** recording what actually happened to their intent.

## The shape

```
intent/<id>  ──▶  integration  ──▶  main  ──▶  production (dark)  ──▶  ramp
                  validated as       human      flag off             1% → 100%
                  a combination      only
```

`references/integration-branch.md` has the full model, the rationale, and the
sources it is drawn from.

## Example prompts

- "Which intents are in the queue and do any of them touch the same files?"
- "Integration is red but every PR was green. What combination broke it?"
- "Write the deploy record for csv-export-20260826 — flag name, ramp, rollback."
- "Is the integration branch earning its keep this quarter?"

## Steps

1. **Check for collisions before anything merges.** Read the `## Files that
   change` list in each in-flight `03-plan.md` and compare them. Two intents
   naming the same path are a collision: sequence them or split the intent. Do
   not discover this in the queue.
2. **Merge accepted intents to `integration`, never to `main`.** Review approval
   moves an intent into the queue; it does not ship it.
3. **Run the checks that only make sense on the combination** — the full test
   suite rather than each PR's affected subset, cross-intent contract and schema
   compatibility, migration ordering when more than one intent carries a schema
   change, and the eval suite when any intent touched agent configuration.
   Batch, build once, test once; do not rebuild per intent.
4. **Treat a red integration branch as an incident.** It blocks every intent
   behind it, so it is never a backlog item. Name the offending combination, not
   just the failing test.
5. **Deploy `integration` to staging on every merge** and check the acceptance
   criteria from each intent's `02-spec.md`. Those checkboxes were written at
   Design precisely to be the human test script here.
6. **Promote to `main` only with human authorization.** `production-gate.sh`
   requires `RELEASE_APPROVAL`, set by a release manager. Never put promotion in
   an agent's instructions, and never let the agent that wrote the code hold the
   token.
7. **Ship dark, then ramp per intent.** Each intent's code reaches production
   behind its own flag, off. Ramp on its own schedule — canary, then a widening
   percentage — watching the metric the intent's spec said would move. Rollback
   is a flag flip, not a revert of a merge containing five other intents.
8. **Tolerate two versions at once** where anything holds long-lived state.
   Shift traffic gradually and keep both versions running rather than cutting
   over; a process mid-flight must not be broken by a promotion.
9. **Write `intents/<id>/05-deploy.md`** from `templates/05-deploy.md`: the
   promotion it rode, the flag, the ramp schedule, the kill switch, who
   authorized it and when. Record the approval reference, never the token value.
10. **Publish queue health where the team reads it** — depth, deploy lag, and
    whether integration is currently green. A queue nobody can see is a queue
    nobody unblocks.

## Anti-patterns

- **Batching intents into a release train.** Then everything waits for the
  slowest intent and rollback unpicks a merge of six. Flags exist so promotion
  and release can be separate events.
- **Automating promotion.** A gate an agent can satisfy is not a gate.
- **Copying per-PR CI onto the integration branch.** Run what the combination
  needs, not the same suite twice.
- **Flags that never reach 100%.** They become permanent untested branches in the
  code. Give every flag an expiry and a removal intent.
- **Keeping the branch out of habit.** If `integration-failure-rate` sits near
  zero for a quarter, the combination is never breaking and `main` should be the
  integration point again. Retire it.

## Output

- An `integration` branch that is always deployable and always deployed to
  staging.
- `intents/<id>/05-deploy.md` per intent: flag, ramp, authorization, rollback.
- A published queue-health signal: depth, deploy lag, current status.
- A collision report for the intents currently in flight.

## Measure

| Indicator | Type | Where it comes from |
|---|---|---|
| `merge-queue-depth` | leading | an external system |
| `deploy-lag` | leading | an external system |
| `integration-failure-rate` | lagging | an external system |
| `flag-ramp-duration` | leading | an external system |

`integration-failure-rate` is the one that decides whether this play is worth
running: it counts how often the combination is red while every individual PR was
green. Near zero for a sustained period means the branch is ceremony.
`deploy-lag` is the one nobody measures — merged is not shipped, and the gap
between them is invisible in PR metrics.

See `references/metrics-catalog.md` for the full indicator set and
`references/integration-branch.md` for the model.
