# The integration branch

How several intents converge and reach production without being batched into a
release.

## The problem this solves

Per-PR CI answers one question: *does this intent work against `main` as it was
when the branch was cut?* It cannot answer the question that actually breaks
you: *do the six intents landing today work together?*

At one or two merges a day that gap is theoretical. At the volume an AI-native
loop produces it is not. Anthropic reports that engineers ship roughly **8x as
much code per quarter** as they did from 2021 to 2025, and that once code
generation stopped being the constraint the bottleneck moved downstream — to
"packaging releases in ways users can understand, and to managing **merge queues
that are suddenly overwhelmed**."

The integration branch is where that convergence is made visible and testable
instead of happening by accident on `main`.

## The model

```
intent/csv-export-20260826    ──┐
intent/rate-limit-20260827    ──┼──▶  integration  ──▶  main  ──▶  production
intent/audit-log-20260827     ──┘         │                │
                                          │                └─ promotion: human only
                                          └─ staging, validated as a set
```

| Branch | What it means | Who moves it |
|---|---|---|
| `intent/<id>` | One intent. Build through Review. Short-lived. | The engineer's session |
| `integration` | Everything accepted but not yet promoted. Deployed to staging. Validated **as a combination**. | The merge queue, automatically |
| `main` | What production runs. | **A human, always** |

Three rules make it work:

1. **An intent branch merges to `integration`, never to `main`.** Review approval
   moves it into the queue; it does not ship it.
2. **`integration` is always deployable and always deployed** — to staging, on
   every merge. A red integration branch is an incident, not a backlog item.
3. **Promotion from `integration` to `main` is human-only.** Never in an agent's
   instructions, never automated, never a hook that can be satisfied by an
   environment variable the agent can set.

## Merge is not release

This is the part that stops the integration branch from becoming a release
train, and it is the practice Anthropic actually describes: most deployments use
**feature flags**, with Claude managing "canary traffic, monitoring for issues,
and automatically ramping a given feature flag up or down."

So an intent's code reaches production **dark**, with the rest of that
promotion, and then ramps on its **own** schedule:

```
merge to integration → staging → promote to main → production (flag off)
                                                      → canary 1% → 10% → 50% → 100%
```

The consequences are worth being explicit about, because they are what make high
merge volume survivable:

- **No batch to assemble.** Nothing waits for a train.
- **Blast radius is per intent, not per release.** Six intents promote together
  and still fail independently.
- **Rollback is a flag flip, not a revert.** No unpicking one intent from a
  merge of six.
- **The human gate moves to the ramp**, where there is real information —
  canary metrics — rather than to the merge, where there is only a diff.

For stateful systems there is a second layer. Anthropic uses **rainbow
deployments** "to avoid disrupting running agents, by gradually shifting traffic
from old to new versions while keeping both running simultaneously," because
"agent systems are highly stateful webs of prompts, tools, and execution logic
that run almost continuously. This means that whenever we deploy updates, agents
might be anywhere in their process." If anything you ship holds long-lived
state, promotion has to tolerate two versions running at once.

## Ordering and collisions

Concurrency is only safe where the work is genuinely independent, and that has to
be determined mechanically rather than remembered. In Anthropic's large-scale
migrations, work is split into "independent file-level units" with "a
deterministic script to produce" the dependency map that decides ordering.

This package already has the raw material: every `03-plan.md` declares its paths
under `## Files that change`. Two in-flight intents naming the same file are a
collision, and you can know that before either one writes code:

```bash
ai-dlc backlog --collisions
```

Sequence them, or split the intent. Do not discover it in the merge queue.

## What the integration branch must run

Not a copy of per-PR CI. The point is the checks that only make sense on the
combination:

- The **full** test suite, not the affected subset each PR ran.
- Cross-intent contract tests: API shapes, schema compatibility, shared fixtures.
- The eval suite, when any intent in the set touched agent configuration.
- Migration ordering, when more than one intent carries a schema change.

Anthropic's migration work serializes the expensive step deliberately rather than
letting every agent trigger it: a build daemon "serializes the most expensive
operation instead of letting multiple agents trigger it independently," batching
patches before rebuilding once and re-running affected tests. Apply the same
logic to the integration branch — batch, build once, test once.

## Keeping the queue healthy

The convergence point needs an owner and a published health signal. Anthropic
runs an agent called **`ci-weather`** that "compiles information from each
incident Slack channel, build metrics, merge queue stats, and deploy lag" and
"posts a newsroom-style report to one public channel anyone in the company can
read."

Four indicators, all external to this repository, all in
`references/metrics-catalog.md`:

| Indicator | Watch for |
|---|---|
| `merge-queue-depth` | A queue that never drains means review is not the bottleneck any more — integration is |
| `deploy-lag` | Merged is not shipped. This gap is invisible in PR metrics |
| `integration-failure-rate` | Red combinations from green PRs. **This is the number that justifies the integration branch — or retires it** |
| `flag-ramp-duration` | Flags that never reach 100% quietly become permanent branches in the code |

## Review at this volume

The integration branch does not reduce review load; it changes where failures
surface. Anthropic scales review by narrowing scope rather than by building one
large reviewer: "Each review agent is designed and scoped to a specific, narrow
focus and leverages RAG for additional context and memory surrounding past
incidents." Coverage was ramped rather than switched on — the share of PRs
receiving substantive review comments "has grown from 16 to 54% as we've gained
confidence in the findings."

Which code gets which treatment is a risk decision, not a uniform policy:
"Tiering our codebase by risk and then automating reviews based on that level,"
with critical paths keeping "strict human approval processes" and the rest
covered by "a risk-weighted sample reviewed by humans."

Separation of duties holds at the promotion gate the same way it holds at merge.
Anthropic's incident-response agent can write docs, post in company channels, and
read production logs, but **cannot deploy**: fixes take "the form of a PR that
the on-call can review, merge, and then deploy."

## When you should not do this

An integration branch is a cost. It is a second place things can be red, a second
queue, and a second thing to own.

**Skip it** when merge volume is low enough that intents rarely land the same day,
when your test suite already runs the full set fast enough on every PR, or when
`integration-failure-rate` sits near zero for a quarter. That last one is the
retirement condition: if the combination is never red when the parts were green,
the branch is ceremony and `main` should be the integration point.

**Keep it** when several intents land per day, when the full suite is too slow to
run per PR, when schema or contract changes are common, or when promotion needs
an artifact a human signs.

## Honest gaps in the evidence

- No Anthropic source describes their merge queue's internal mechanics — only
  that one exists and that its stats are published. Whether it batches or
  serializes is unconfirmed, so the batching guidance above is inference from
  their migration tooling, not a documented practice.
- The branch topology here is this package's recommendation. Anthropic documents
  feature flags, canary ramping, rainbow deployments, and a monitored merge
  queue; the three-branch layout is our synthesis of those into something a
  smaller team can run.
- A widely repeated "five releases per engineer per day" figure traces to a
  paywalled secondary post and is **not** cited here.

## Sources

- [The AI-Native SDLC playbook](https://claude.com/blog/the-ai-native-sdlc-playbook)
- [How Claude Tag serves as Anthropic's first responder for CI/CD failures](https://claude.com/blog/ai-ci-cd-on-call) — `ci-weather`, feature flags, canary ramping, on-call review
- [How Anthropic secures its AI-native software development lifecycle](https://claude.com/blog/how-anthropic-secures-its-ai-native-software-development-lifecycle) — narrow review agents, risk tiering, 16→54%, separation of duties
- [How Anthropic runs large-scale code migrations with Claude Code](https://claude.com/blog/ai-code-migration) — dependency maps, resumable queues, serialized builds, adversarial reviewers
- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) — rainbow deployments
- [Anthropic says 80% of its new production code is now authored by Claude](https://venturebeat.com/technology/anthropic-says-80-of-its-new-production-code-is-now-authored-by-claude-how-your-enterprise-can-keep-up) — the review bottleneck
