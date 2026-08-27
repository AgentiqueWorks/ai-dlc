---
name: 06-closing-the-loop
description: Respond to production or process control-band breaches by diagnosing and writing a new intent.md that re-enters the SDLC loop. Use in the Maintain stage.
---

# Closing the loop

## Job

Watch a metric, detect a breach, and let the agent propose a fix without a human starting the process.

## Who uses this

- **SREs** who want incidents to open `intent.md` automatically.
- **Platform engineers** running `bands.yaml` monitors.
- **Engineering managers** tracking process metrics like PR cycle time.

## Example prompts

- "The post-deploy 5xx rate is at 3σ. Open an `intent.md` and a PR or a rollback."
- "PR cycle time has drifted. Write a report for engineering leadership."
- "The CI failure rate breached 2σ. Diagnose with GitHub logs."

## Steps

1. Read `bands.yaml` and the latest metric values from Datadog, GitHub, or another store.
2. At 1σ, log only. At 2σ, run a read-only diagnosis. At 3σ, propose action.
3. Allowed 3σ actions: open a PR, trigger an approved runbook (e.g. `rollback-deploy`), or escalate to a human.
4. Use `datadog` or `sentry` MCP to gather evidence; use `pagerduty` to acknowledge if applicable.
5. Write the diagnosis and proposal as `intent.md` using `templates/intent.md`.
6. Route product-facing findings to the PM; route pure-ops findings to the on-call engineer.

## Output

- A new `intent.md` in the triage queue.
- A log of breach, tier, and action taken.