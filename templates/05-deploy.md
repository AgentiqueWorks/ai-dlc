# Deploy: <title>

- **From review:** `intents/<id>/04-review.md`
- **Status:** in-progress
- **Merged to integration:** <YYYY-MM-DDTHH:MM:SSZ>
- **Promoted to main:** <YYYY-MM-DDTHH:MM:SSZ>
- **Release:** <tag or commit>

<!--
Merged is not shipped. This intent reaches production dark, behind its own flag,
alongside whatever else was promoted in the same batch — and then ramps on its
own schedule. Record both events; deploy-lag is the gap between them.
-->

## Promoted with

Other intents in the same promotion. They shipped together and must be able to
fail apart.

- `intents/<other-id>/` — <title>

## Gate

- **Gate that ran:** <hook name, e.g. production-gate.sh>
- **Approval reference:** <RELEASE_APPROVAL record id — the reference, never the token value>
- **Authorized by:** <release manager — never the agent, never the author>
- **Authorized at:** <YYYY-MM-DDTHH:MM:SSZ>

## Flag

- **Name:** `<flag_key>`
- **Default:** off
- **Owner:** <who ramps it>
- **Expiry:** <YYYY-MM-DD — the date this flag is removed, not "when we get to it">
- **Removal intent:** `intents/<id>/01-intent.md` <or: to be filed at 100%>

A flag with no expiry becomes a permanent untested branch in the code. Give it a
date and an intent that deletes it.

## Ramp

| Stage | Audience | Started | Held for | Decision |
|---|---|---|---|---|
| dark | 0% | | | |
| canary | <1%, or an internal workspace> | | | |
| partial | <10%> | | | |
| full | 100% | | | |

**Watch during ramp:** <the specific metric the spec said would move, plus the
guardrail metrics that must not move.>

## Stateful concerns

- **Long-running work in flight?** <yes/no — if yes, both versions must run
  simultaneously and traffic shift gradually, rather than cutting over>
- **Schema or contract change?** <yes/no — if yes, name the ordering constraint
  against the other intents in this promotion>

## Verification

Acceptance criteria come from `intents/<id>/02-spec.md`. They were written at
Design to be checked here.

- [ ] <criterion from the spec>
- [ ] <guardrail metric within its band>

## Rollback

- **Mechanism:** flag off — <the default; a revert is only needed for changes a
  flag cannot cover, such as a migration>
- **Trigger:** <the condition that means roll back, stated as a threshold>
- **Owner:** <who flips it>
- **Runbook:** <path or url, for the non-flag case>

## Outcome

- **Result:** <shipped | rolled back | partial | still ramping>
- **Deploy lag:** <merge to production, computed from the timestamps above>
- **Notes:** <what actually happened>
