---
name: platform-metrics
description: Measure whether the AI-native SDLC is actually working, using leading and lagging indicators per stage — computing what the repository can compute and naming the source for what it cannot. Use monthly, or when deciding which play to adopt next.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Edit
  - Bash(ai-dlc:*)
  - Bash(git log:*)
  - Bash(git diff:*)
  - Bash(gh pr list:*)
metadata:
  stage: "platform"
  persona: "tech-lead, platform, product-owner, service-owner"
  requires: "01-intent-capture, 03-plan-mode"
  produces: "metrics/"
  indicators: "artifact-chain-completeness, stage-latency, plan-diff-alignment, rework-after-review, intent-survival, intent-staleness, spec-churn, time-to-intent"
  mcp: "github, gitlab, datadog"
  maturity: "beta"
---

# Measurement

## Job

Report whether the loop is getting faster and better, using indicators that
trigger a decision — and be explicit about which numbers the repository can
compute and which have to come from somewhere else.

## Who uses this

- **Tech leads** deciding which play to adopt next.
- **Platform engineers** reporting on the rollout.
- **Product and service owners** who want the delivery picture, not a token count.

## Leading and lagging

Every stage has both, and they answer different questions:

- **Leading** indicators move first and tell you whether a play is being
  practised. `time-to-intent`, `stage-latency`, `ci-first-pass-rate`.
- **Lagging** indicators move later and tell you whether it worked.
  `plan-diff-alignment`, `change-failure-rate`, `repeat-incidents`.

A leading indicator moving without its lagging pair is adoption without benefit —
the most common failure, and the one worth catching early.

## Example prompts

- "Run our AI-DLC metrics and tell me which stage is the bottleneck."
- "Plan-diff alignment dropped this month. Why?"
- "Which indicators can we actually compute, and which need Datadog?"

## Steps

1. **Compute what the repository knows.**

   ```
   ai-dlc metrics
   ai-dlc metrics --json > metrics/$(date +%Y-%m).json
   ```

   Eight indicators come from the `intents/` tree and git history alone. Run it
   with full history; a shallow clone suppresses the history-derived ones rather
   than reporting a wrong number.

2. **Read the catalog for the rest.** `references/metrics-catalog.md` lists every
   indicator the playbook names, its stage, whether it leads or lags, and — for
   the ones this package cannot compute — exactly which system owns it.

3. **Fill in the external numbers by hand, with their source.** Use
   `templates/metrics.md`. A number with no named source is not a measurement.

4. **Find the bottleneck, not the average.** Read `stage-latency` per stage.
   The stage with the largest median is where the loop is actually queuing, and it
   is usually a human gate rather than the agent.

5. **Read the pairs, not the singles.**

   | If this rises | And this rises | It means |
   |---|---|---|
   | `changes-per-engineer` | `rework-after-review` | Throughput bought with rework |
   | `artifact-chain-completeness` | `stage-latency` | Ceremony without speed |
   | `intent-survival` | `intent-staleness` | Capture outrunning triage |
   | `eval-pass-rate` | `repeat-incidents` | Evals testing the wrong things |

6. **Turn each moved indicator into a decision with a home.** `templates/metrics.md`
   ends with a table for exactly this: indicator, direction, decision, and the
   file the change lands in — a skill, a hook, `CLAUDE.md`, an eval. An indicator
   that changes no file changed nothing.

7. **Set a floor in CI where it is worth it.**

   ```
   ai-dlc metrics --fail-under-alignment 0.7
   ```

   Use this sparingly. A threshold on a metric people can game gets gamed;
   `plan-diff-alignment` is safe to floor because the cheap way to satisfy it is
   to keep the plan accurate, which is the behaviour you want.

8. **Recheck the adoption order.** `ai-dlc adoption` shows which plays are
   unlocked. A stage whose indicators are flat is often waiting on a prerequisite
   play, not on more effort.

## Honesty rules

- Never report an indicator whose source you cannot name.
- Never report a history-derived number from a shallow clone.
- `intent-survival` is approximate: squash-merged branches that never landed
  `intents/` are invisible to it. Say so when you report it.
- Report `n` alongside every median. A median of two samples is an anecdote.

## Output

- `metrics/<YYYY-MM>.json` — the computed indicators, committed.
- A filled `templates/metrics.md` report naming the source of every external
  number.
- A decision table: for each indicator that moved the wrong way, the change and
  the file it lands in.

## Measure

| Indicator | Type | Where it comes from |
|---|---|---|
| `artifact-chain-completeness` | leading | `ai-dlc metrics` |
| `stage-latency` | leading | `ai-dlc metrics` |
| `plan-diff-alignment` | lagging | `ai-dlc metrics` |
| `rework-after-review` | lagging | `ai-dlc metrics` |
| `intent-survival` | lagging | `ai-dlc metrics` |
| `intent-staleness` | leading | `ai-dlc metrics` |
| `spec-churn` | lagging | `ai-dlc metrics` |
| `time-to-intent` | leading | `ai-dlc metrics` (needs an extra field) |

`references/indicator-recipes.md` gives the exact commands behind each one, so a
number can always be traced back to the git query that produced it.

See `references/metrics-catalog.md` for the full indicator set.
