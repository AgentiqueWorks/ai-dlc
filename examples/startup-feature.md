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

**Release manager**: `/05-release-gate`
`production-gate.sh` holds the deploy until `RELEASE_APPROVAL` is set. The
authorization, the staged rollout, and the rollback trigger go into
`05-deploy.md`.

**SRE**: Deployment is verified via the `vercel` and `sentry` MCP servers.
`06-closing-the-loop` watches the control bands in `bands.yaml`.

**The loop closes.** `06-lessons.md` records what changed in the agent's
configuration, not just what was learned: the missing input validation became a
rule in the security skill, and the streaming requirement became a line in
`CLAUDE.md` and a regression eval. The next intent starts with both already in
place.

See the complete chain in `examples/intents/csv-export-20260826/`, and measure it
with:

```bash
ai-dlc backlog
ai-dlc metrics --intent csv-export-20260826
```