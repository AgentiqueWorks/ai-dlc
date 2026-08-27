# Deploy: CSV export for the reports table

- **From review:** `intents/csv-export-20260826/04-review.md`
- **Status:** done
- **Merged to integration:** 2026-08-26T14:05:00Z
- **Promoted to main:** 2026-08-26T16:40:00Z
- **Release:** `v2.14.0` (`a91f3c2`)

## Promoted with

- `intents/rate-limit-20260826/` — Per-workspace rate limiting

Both touched `src/api/reports/`, so the collision check ran before either
branched. The plans did not overlap on any file, and the integration branch was
green on the combination.

## Gate

- **Gate that ran:** `production-gate.sh`
- **Approval reference:** `REL-2026-0826-03`
- **Authorized by:** Dana Okafor, release manager
- **Authorized at:** 2026-08-26T16:38:00Z

## Flag

- **Name:** `csv_export`
- **Default:** off
- **Owner:** Priya Raman
- **Expiry:** 2026-09-30
- **Removal intent:** `intents/remove-csv-export-flag-20260930/01-intent.md`

## Ramp

| Stage | Audience | Started | Held for | Decision |
|---|---|---|---|---|
| dark | 0% | 2026-08-26T16:40Z | 12m | promoted clean, no traffic |
| canary | internal workspace only | 2026-08-26T16:52Z | 30m | p99 1.9s against a 3s budget |
| partial | 10% | 2026-08-26T17:25Z | 45m | no new Sentry groups |
| full | 100% | 2026-08-26T18:10Z | — | held 24h, flag removal scheduled |

**Watched during ramp:** export p99 latency, error rate on `/api/reports/*`, and
memory on the export workers — the streaming change was the risk the plan named.

## Stateful concerns

- **Long-running work in flight?** Yes. Exports can run for minutes, so both
  versions ran simultaneously and traffic shifted gradually rather than cutting
  over. No export was interrupted by the promotion.
- **Schema or contract change?** No.

## Verification

- [x] `/api/reports/export` returns 200 with a `text/csv` body
- [x] Empty result set returns headers only and does not crash
- [x] p99 latency on `/api/reports` within 1 sigma of the 30-day baseline
- [x] No new Sentry issue groups during the ramp

## Rollback

- **Mechanism:** flag off — `csv_export=false`, no revert needed
- **Trigger:** error rate on `/api/reports/*` above 2 sigma for five minutes
- **Owner:** on-call engineer
- **Runbook:** `runbooks/rollback-deploy.md`

## Outcome

- **Result:** shipped
- **Deploy lag:** 2h 35m from merge on integration to production, of which 2h 20m
  was waiting for the release manager. That wait is the number worth attacking,
  not the ramp.
- **Notes:** Ramped to 100% in 1h 30m with no rollback. The rate-limit intent
  promoted in the same batch and ramped on its own schedule the next morning,
  which is the point of shipping dark.
