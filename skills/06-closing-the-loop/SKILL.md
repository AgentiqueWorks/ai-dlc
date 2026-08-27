---
name: 06-closing-the-loop
description: Respond to production or process control-band breaches by diagnosing and writing a new intent.md that re-enters the SDLC loop. Use in the Maintain stage.
---

# Closing the loop

## Job

Watch a metric, detect a breach, and let the agent propose a fix without a human starting the process.

## Steps

1. Read `bands.yaml` and the latest metric values from the configured store (Prometheus, CI API, PR metrics).
2. At 1σ, log only. At 2σ, run a read-only diagnosis. At 3σ, propose action.
3. The allowed 3σ actions are: open a PR, trigger an approved runbook (e.g. rollback-deploy), or escalate to a human.
4. Write the diagnosis and proposal as `intent.md` using `templates/intent.md`.
5. Route product-facing findings to the product owner; route pure-operations findings to the on-call engineer.

## Output

- A new `intent.md` in the triage queue.
- Log of breach, tier, and action taken.