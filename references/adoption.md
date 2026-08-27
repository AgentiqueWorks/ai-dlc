# Adoption order

Some plays have no prerequisites. Others quietly assume one, and adopting them
early produces effort without benefit — an automated review loop before the
review is any good just automates the noise.

The dependency graph lives in each skill's `metadata.requires`, so it is one
source of truth rather than a diagram that drifts. Derive it whenever you want:

```bash
ai-dlc adoption
ai-dlc adoption --mermaid
```

## Start here — no prerequisites

These four can begin today, in any order, independently of each other.

| Play | What changes on day one |
|---|---|
| `01-intent-capture` | Ideas and tickets arrive as a committed `intent.md` instead of a conversation |
| `03-claude-md` | Sessions stop guessing your build and test commands |
| `03-org-skills` | The policy people keep re-explaining becomes something the agent applies |
| `05-release-gate` | The operations you would not want happening unattended stop happening unattended |

`03-claude-md` is the highest-leverage of the four. Almost everything downstream
gets better when the agent knows how the repository actually works, and nothing
downstream works well while it does not.

## Then, roughly in this order

1. **`02-spec-writer`** — once intents exist to write specs from.
2. **`04-feedback-loop`** — once `CLAUDE.md` names the commands to run. This is
   the play that stops sessions claiming done without checking.
3. **`03-plan-mode`** — once there is a spec to plan from. Now
   `plan-diff-alignment` becomes measurable, which is the best single signal you
   will get about whether any of this is working.
4. **`03-subagents`** — once jobs are recurring often enough to be worth scoping.
5. **`04-continuous-evals`** — once the feedback loop works. Configuration steers
   the agent; this is the play that regression-tests it.
6. **`05-pr-review`** — once plans and `CLAUDE.md` are good enough that findings
   are worth reading.
7. **`05-managed-settings`** — when the rollout leaves one team and rules need to
   hold everywhere.
8. **`05-integration`** — the moment more than one intent lands per day. Before
   that, per-PR CI is enough and an integration branch is pure cost. After it,
   you are testing each intent against a `main` that no longer reflects what is
   about to ship alongside it.
9. **`05-cicd-integration`** — once review and gates are established. Automating
   an immature review loop scales the noise.
10. **`05-cicd-triage`** — once CI is where failures are diagnosed.
11. **`03-parallel-sessions`** — only once `CLAUDE.md`, tests, and hooks are
    mature. Parallelism multiplies whatever your guardrails already do, in both
    directions.
12. **`platform-metrics`** — as soon as there are intents and plans to measure. Early
    numbers with small `n` are still useful for finding the bottleneck stage.
13. **`06-closing-the-loop`** — last of the maintenance plays, because it needs
    the intent format, the review gate, hooks, CI integration, and a rollback
    path all in place.
14. **`06-security-scan`**, **`06-on-call`** — after the loop closes, using the
    same gates and the same intent format.

## Signals you moved too fast

| Symptom | The play you skipped |
|---|---|
| Review findings are ignored | `05-pr-review` before `03-claude-md` matured |
| Sessions claim done and are not | `04-feedback-loop` |
| Plans and diffs disagree constantly | `02-spec-writer` — planning from an unclear spec |
| Parallel sessions collide | Overlapping `## Files that change`; sequence them |
| A gate everybody works around | `hook-wait-time` — see `observability.md` |
| Merges are green but `main` keeps breaking | `05-integration` — nothing tests the combination |
| Rollback means reverting other people's work too | Shipping without feature flags; see `integration-branch.md` |
| Evals pass while incidents repeat | Evals written from imagination, not from incidents |

## Signals you are ready for the next one

- `artifact-chain-completeness` stops rising because everything is at the same
  stage — the next play is the one that produces the next artifact.
- `stage-latency` has one stage far above the others — that stage is queuing, and
  it is usually a human gate rather than the agent.
- An indicator has been flat for two months — the play it measures is probably
  waiting on a prerequisite, not on more effort.

`ai-dlc adoption` prints the waves; `ai-dlc metrics` tells you which one you are
actually in.
