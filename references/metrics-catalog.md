# Metrics catalog

The playbook names roughly thirty indicators across the six stages. This is the
prose companion to `indicators.yaml`, which is the machine-readable source of
truth that `ai-dlc metrics` and `ai-dlc validate` both read.

Run `ai-dlc metrics --list-indicators` to see the current state of every one.

## How to read this

**Leading** indicators move first and tell you whether a play is being practised.
**Lagging** indicators move later and tell you whether it worked. Read them in
pairs: a leading indicator moving on its own is adoption without benefit.

`computable` says how far this package can go on its own:

| Value | Meaning |
|---|---|
| `git-free` | Derived from the `intents/` tree alone |
| `git` | Derived from local git history |
| `conditional` | Computable only when the artifact carries an extra field |
| `external` | Needs an API this package does not talk to |

Nothing marked `external` is estimated, inferred, or filled in with a plausible
number. It is reported as `n/a` with the system that owns it named, and
`templates/metrics.md` has a place to record it by hand.

## Computed by `ai-dlc metrics`

| Indicator | Stage | Type | Source |
|---|---|---|---|
| `artifact-chain-completeness` | all | leading | Which of the six artifacts exist per intent |
| `time-to-intent` | Plan | leading | `- **Signal at:**` vs. the commit that added `01-intent.md` |
| `intent-survival` | Plan | lagging | Intents that reached the default branch (approximate) |
| `intent-staleness` | Plan | leading | Days since the intent folder was last touched |
| `stage-latency` | Design | leading | First-add timestamps between consecutive artifacts |
| `spec-churn` | Design | lagging | Commits to `02-spec.md` after `03-plan.md` landed |
| `plan-diff-alignment` | Build | lagging | `## Files that change` vs. the real diff |
| `rework-after-review` | Test | lagging | Commits on the branch after `04-review.md` landed |

`references/indicator-recipes.md` inside the `platform-metrics` skill gives the exact
git command behind each one.

### The two caveats worth stating out loud

**`intent-survival` is approximate.** It defines "landed" as `01-intent.md`
reaching the default branch. A team that squash-merges and deletes branches
without landing `intents/` will show 0% survival while shipping perfectly well.
If that is your workflow, this indicator is measuring your merge strategy.

**`time-to-intent` needs a field you have to fill in.** The moment a customer
message or an alert arrived is not in git. `templates/01-intent.md` carries a
`Signal at` line for it. Left as a placeholder, the indicator reports `n/a` — it
never guesses from the commit alone.

## Documented only — read these from the system that owns them

| Indicator | Stage | Type | Owning system |
|---|---|---|---|
| `first-pass-implementation` | Build | leading | PR API |
| `ci-first-pass-rate` | Test | leading | CI |
| `eval-pass-rate` | Test | leading | Eval run history |
| `regressions-caught-in-ci` | Test | lagging | CI + incident tracker |
| `pr-review-time` | Deploy | lagging | PR API |
| `hook-wait-time` | Deploy | leading | OpenTelemetry — see `observability.md` |
| `gate-violations` | Deploy | lagging | Incident tracker, before/after each gate |
| `change-failure-rate` | Deploy | lagging | Incident tracker (DORA) |
| `dora` | Deploy | lagging | Deploy frequency, lead time, CFR, MTTR |
| `band-breach-to-intent` | Maintain | leading | Bands detector vs. the triage queue |
| `findings-to-fixes` | Maintain | lagging | Triage queue vs. PR history |
| `repeat-incidents` | Maintain | lagging | Incident tracker, by incident class |
| `scan-coverage` | Maintain | leading | Security scanning inventory |
| `finding-to-patch-time` | Maintain | leading | Scan history + PR metadata |
| `vulns-in-prod-vs-scan` | Maintain | lagging | Incident tracker |
| `findings-per-scan` | Maintain | lagging | Scan history trend |
| `concurrent-sessions` | Platform | leading | OpenTelemetry |
| `changes-per-engineer` | Platform | lagging | PR history |
| `onboarding-first-pr` | Platform | lagging | PR history |
| `skill-merge-time` | Platform | leading | PR history, from policy-owner approval |
| `policy-cite-findings` | Platform | lagging | Review findings |

## Reading the pairs

| If this rises | And this rises | It means |
|---|---|---|
| `changes-per-engineer` | `rework-after-review` | Throughput bought with rework |
| `artifact-chain-completeness` | `stage-latency` | Ceremony without speed |
| `intent-survival` | `intent-staleness` | Capture is outrunning triage |
| `eval-pass-rate` | `repeat-incidents` | The evals test the wrong things |
| `concurrent-sessions` | `pr-review-time` | Parallelism has moved the bottleneck to review |

## Rules for reporting

1. Never report an indicator whose source you cannot name.
2. Never report a history-derived number from a shallow clone. `ai-dlc metrics`
   detects this and suppresses those indicators rather than reporting a
   confidently wrong figure; `actions/checkout` needs `fetch-depth: 0`.
3. Report `n` alongside every median. A median of two samples is an anecdote.
4. An indicator that changes no file changed nothing. `templates/metrics.md` ends
   with a decision table for exactly this reason.

## Thresholds

Use them sparingly, and only where the cheapest way to satisfy the threshold is
the behaviour you actually want:

```
ai-dlc metrics --fail-under-alignment 0.7
ai-dlc metrics --fail-under-completeness 0.5
```

`plan-diff-alignment` is safe to floor: the cheap way to pass is to keep the plan
accurate. `artifact-chain-completeness` is not, if you gate it too early — the
cheap way to pass is to write empty artifacts.
