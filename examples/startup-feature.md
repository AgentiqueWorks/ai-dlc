# Startup feature: CSV export

## Scenario

A three-person SaaS team needs to ship a CSV export button for reports. Everyone wears multiple hats, so the same engineer may capture intent, write the spec, and implement.

## Transcript

**PM in Intercom**: "Customers keep asking for CSV exports."

**PM**: `/01-intent-capture`  
Agent pulls the Intercom thread and writes `intent/2026-08-26-csv-export.md`.

**PM**: `/02-spec-writer`  
Agent reads the intent, pulls the Figma mock, and writes `spec.md`.

**Engineer**: `/03-plan-mode`  
Agent writes `plan.md`:

```markdown
# Plan: CSV export

## Files that change
- `report/page.tsx`
- `report/export.ts`
- `report/export.test.ts`

## Order of work
1. Add `toCsv` helper in `report/export.ts`.
2. Add a button in `report/page.tsx`.
3. Add tests for zero, one, and many rows.

## Risks
- Empty data set must not crash.
- Existing PDF export must remain untouched.

## Proof
- `npm test report/export.test.ts` passes.
- Playwright screenshot shows the new button.
```

**Engineer**: Accepts the plan, the agent implements, and `04-feedback-loop` runs the proof.

**Tech lead**: `/05-pr-review`  
Agent finds: "Important: the CSV endpoint does not validate input." The engineer fixes it; the lead merges.

**SRE**: Deployment is verified via `vercel` and `sentry` MCP. `06-closing-the-loop` watches for spikes.