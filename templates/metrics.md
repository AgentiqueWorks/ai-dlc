# Delivery indicators: <team or service>

- **Period:** <YYYY-MM-DD to YYYY-MM-DD>
- **Generated:** run `ai-dlc metrics --markdown` and paste the table below
- **Owner:** <who reads this and acts on it>

## Computed from the repository

<!-- paste the output of `ai-dlc metrics --markdown` here -->

## Read from external systems

The playbook names indicators this repository cannot compute on its own. Fill
these in from the systems that own them, and record where each number came from.

| Indicator | Value | Source system | Notes |
|---|---|---|---|
| CI test pass rate, first pass | | <CI> | |
| PR review time | | <forge> | |
| Eval pass rate | | eval history | |
| Hook wait time | | OpenTelemetry | |
| Change failure rate | | incident tracker | |
| DORA: deploy frequency, lead time, CFR, MTTR | | <source> | |

## What we are changing because of this

Indicators exist to trigger a decision. For each one that moved the wrong way,
name the change and where it lands.

| Indicator | Direction | Decision | Lands in |
|---|---|---|---|
| <name> | <up/down> | <what we will do> | `CLAUDE.md` / a skill / a hook / an eval |
