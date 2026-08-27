# Deploy: CSV export for the reports table

- **From review:** `intents/csv-export-20260826/04-review.md`
- **Status:** done
- **Environment:** production
- **Release:** `v2.14.0` (`a91f3c2`)

## Gate

- **Gate that ran:** `production-gate.sh`
- **Approval token:** `RELEASE_APPROVAL=REL-2026-0826-03` (the record; the value is not stored here)
- **Authorized by:** Dana Okafor, release manager
- **Authorized at:** 2026-08-26T16:40:00Z

## Rollout

1. Merge `intent/csv-export-20260826` to `main`; Vercel builds the preview.
2. Promote the preview to production.
3. Enable `csv_export` for the internal workspace only.
4. Enable for all workspaces after 30 minutes at baseline.

## Verification after deploy

- [x] `/api/reports/export` returns 200 with a `text/csv` body
- [x] p99 latency on `/api/reports` within 1 sigma of the 30-day baseline
- [x] No new Sentry issue groups in the 30 minutes after promotion

## Rollback

- **Runbook:** `runbooks/rollback-deploy.md`
- **Trigger:** error rate on `/api/reports/*` above 2 sigma for five minutes
- **Owner:** on-call engineer

## Outcome

- **Result:** shipped
- **Notes:** Staged rollout completed at 17:25Z. Export p99 was 1.9s on the
  largest internal workspace, against a 3s budget.
