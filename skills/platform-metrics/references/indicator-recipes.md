# Indicator recipes

Every number `ai-dlc metrics` reports traces back to a command you can run
yourself. If a number looks wrong, run the recipe and find out why.

## Author dates, not committer dates

All timestamps use `%aI`. A rebase rewrites the committer date; the author date
survives. What we are measuring is when a person produced the artifact, so the
author date is the correct one — and it means a rebased branch still reports
honest latency.

## artifact-chain-completeness

No git involved. Count the files present under `intents/<id>/` against the six
the chain defines.

```
ls intents/*/ | sort
```

Reads 100% only when `05-deploy.md` and `06-lessons.md` exist too. Most teams sit
at 4/6 until they adopt the release gate and the closing-the-loop play — that is
information, not an error.

## stage-latency

First-add time of each artifact, from a single pass over history:

```
git log --all --diff-filter=A --reverse --format='C%x09%aI' --name-only -- intents/
```

The difference between consecutive artifacts in one intent is that stage's
latency. Reported as a median with `n`; a median of two is an anecdote.

## plan-diff-alignment

The strongest local signal, and the one worth reading first.

```
git merge-base main intent/<id>
git diff --name-only $(git merge-base main intent/<id>)...intent/<id>
```

Compared against the bullets under `## Files that change` in `03-plan.md`, with
`intents/` paths excluded. A path in the plan matches a changed file exactly, or
as a directory prefix.

Three ways it degrades, all reported rather than hidden:

- The plan has no `## Files that change` section → intent skipped, listed under
  `detail.skipped`.
- The branch was squash-merged and deleted → falls back to default-branch commits
  that touched `intents/<id>/`, which is exactly right for a squash merge, and
  the result is flagged `approximate`.
- Shallow clone → not computed at all.

## rework-after-review

Commits on the intent branch, after `04-review.md` first appeared, that touched
something other than `intents/`.

```
git log --format='C%x09%H%x09%aI' --name-only $(git merge-base main intent/<id>)..intent/<id>
```

This is a local proxy for the playbook's "rework cycles per change", which needs
PR metadata. It is named for what it actually measures.

## intent-survival

"Landed" means `intents/<id>/01-intent.md` reached the default branch:

```
git log --first-parent main --diff-filter=A --reverse --format=%aI -- intents/<id>/01-intent.md
```

`--first-parent` makes this correct under both merge commits and squash merges.

**Approximate, and say so:** a team that squash-merges and never lands `intents/`
will show 0% survival while shipping fine. If that is your workflow, this
indicator is measuring your merge strategy, not your delivery.

## intent-staleness

Last commit touching the intent folder, against `--stale-days` (default 30).
Landed intents are excluded — an intent that shipped is not stale.

## spec-churn

Commits touching `02-spec.md` after `03-plan.md` first appeared. Requirements
still moving after the plan was committed means the spec advanced to Build too
early.

## time-to-intent

The only conditional indicator. It needs `- **Signal at:** <ISO8601>` in
`01-intent.md`, because the moment a customer message or alert arrived is not in
git. Reported as `n/a` with a note when the field is absent — never estimated
from the commit alone.

## What is not computable here

`ci-first-pass-rate`, `pr-review-time`, `eval-pass-rate`, `hook-wait-time`,
`change-failure-rate`, `gate-violations`, the DORA set, and the security-scan
indicators all need an API this package does not talk to.

```
ai-dlc metrics --list-indicators
```

shows every indicator and whether it is implemented. `validate` enforces that
this stays true: an indicator cannot claim to be computable without an
implementation, and an implementation cannot exist without a catalog entry.
