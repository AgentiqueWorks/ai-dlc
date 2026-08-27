# Team usage flows

This document shows how different roles use the skills in this repo. It covers a startup scenario and an enterprise scenario. Artifacts are named
by their position in the chain: `01-intent.md`, `02-spec.md`, `03-plan.md`,
`04-review.md`, `05-deploy.md`, `06-lessons.md`, all under `intents/<id>/`.

## Personas and their first skill

| Persona | First skill they touch | Main MCP servers | Goal |
|---|---|---|---|
| Originator / PM | `01-intent-capture` | Slack, Intercom, Jira, Notion | Capture a problem as `01-intent.md`. |
| Product owner | `02-spec-writer` | Figma, Notion, Confluence | Decide whether an intent advances, and sign off `02-spec.md`. |
| Designer | `02-spec-writer` | Figma, Notion, Confluence | Co-write the spec and attach mocks. |
| Engineer | `03-plan-mode` | GitHub, GitLab | Turn `02-spec.md` into `03-plan.md` and implement. |
| Engineer (scale) | `03-subagents`, `03-parallel-sessions` | GitHub | Scope recurring jobs; run independent intents in worktrees. |
| Policy owner | `03-org-skills` | Notion, Confluence | Make security, API, brand, and UX rules operational. |
| QA / Test engineer | `04-continuous-evals` | Playwright, GitHub | Regression-test the agent's configuration. |
| Tech lead | `05-pr-review` | GitHub, GitLab | Own `REVIEW.md`; read findings and decide. |
| Release manager | `05-release-gate`, `05-integration` | GitHub, Vercel | Authorize promotion; record the flag and ramp in `05-deploy.md`. |
| Platform engineer | `03-claude-md`, `05-managed-settings`, `05-cicd-integration` | GitHub, GitLab | Agent memory, non-overridable policy, pipeline wiring. |
| SRE / Service owner | `06-closing-the-loop` | Datadog, PagerDuty, Slack | Define control bands; respond to breaches. |
| Security lead | `06-security-scan` | Sentry, GitHub, Jira | Own the security skill; route scan findings. |
| Tech lead / Platform | `platform-metrics` | GitHub, Datadog | Decide which play to adopt next, from evidence. |

Who is accountable for which decision — and which decisions an agent must never
make — is in `roles.md`. The order to adopt the plays in is in `adoption.md`.

## Startup example: shipping a new feature

### 1. PM captures intent from a customer chat (10 minutes)

A customer says in Intercom: "I cannot export my reports to CSV." The PM opens the agent and runs:

```
/01-intent-capture
```

The agent:

- Pulls the Intercom conversation via the `intercom` MCP server.
- Asks the PM two clarifying questions: "Which report types?" and "Should this be in-app or email?"
- Writes `intent/2026-08-26-export-csv.md` using `templates/intent.md`.
- Proposes: add a CSV export button on the report page, keep existing PDF export, no email for now.

### 2. PM and Designer write the spec (30 minutes)

The PM runs:

```
/02-spec-writer
```

The agent:

- Reads the accepted `intent.md`.
- Pulls the existing report page from the Figma file via `figma` MCP.
- Drafts `spec.md` with requirements, design, acceptance criteria, and the constraint: "Use the existing design system; no new components."
- Flags one concern: the PDF export currently uses an older component; the new CSV button may need a consistent placement.
- The designer reviews and resolves the concern; the spec is committed.

### 3. Engineer creates a plan and implements (1–2 hours)

The engineer runs:

```
/03-plan-mode
```

The agent:

- Reads `spec.md` and `CLAUDE.md`.
- Inspects the repo via `Read`/`Grep`.
- Writes `plan.md`:
  - Files: `report/page.tsx`, `report/export.ts`, `report/export.test.ts`
  - Order: add backend CSV generator, wire UI button, add tests
  - Proof: `npm test report/export.test.ts` and a screenshot of the button
- The engineer accepts the plan; the agent implements in auto mode.
- `04-feedback-loop` runs `npm test` and `playwright` to screenshot the new button.

### 4. Continuous evals keep the build safe (ongoing)

QA runs:

```
/04-continuous-evals
```

The agent:

- Writes an eval for the CSV export in `evals/csv-export.json`.
- Adds a check that the export still works when the report has zero rows.
- The eval becomes a CI gate on future `CLAUDE.md` or skill changes.

### 5. PR review (15 minutes)

The tech lead runs:

```
/05-pr-review
```

The agent:

- Loads the diff, `spec.md`, and `plan.md`.
- Runs bug, security, and compliance passes.
- Reports: "Important: the CSV endpoint does not validate input." The engineer fixes it.
- The human approves and merges.

### 6. Deploy and observe (5 minutes)

The SRE has `vercel` MCP configured. The deployment is triggered through the existing pipeline. `06-closing-the-loop` watches Datadog and Sentry. If the CSV export error rate spikes, it opens a new `intent.md`.

## Enterprise example: a regulated change

### 1. Intent from a Jira change request

A PM receives `JIRA-4822`: "Add audit logging to payment events." The PM runs `/01-intent-capture`. The agent pulls the Jira ticket, confirms constraints (PCI scope, no PII in logs), and writes `intent/payment-audit.md`.

### 2. Design with compliance skills

The PM runs `/02-spec-writer`. The agent loads the security and compliance skills and flags: "Audit events must include actor, action, entity, and timestamp; PII must not appear in logs." The security policy owner resolves the flag.

### 3. Plan with an approval gate

The engineer runs `/03-plan-mode`. The agent writes `plan.md` and proposes touching `payments/events.rs` and `audit/schema.sql`. The plan is routed to the security architect for higher-risk sign-off.

### 4. Build with hooks

Implementation runs under `.claude/hooks/` that block edits to `schema.sql` without a change-ticket number and that run the formatter after edits.

### 5. Review and release gates

`/05-pr-review` runs. `/05-release-gate` blocks the production deploy until `RELEASE_APPROVAL` is set. The change-advisory board authorizes the release; the gate passes.

### 6. Maintain and audit

Security runs `/06-security-scan` on a schedule. SRE runs `/06-closing-the-loop` with Datadog and PagerDuty. Every finding and fix is written back as an `intent.md` or PR, preserving the audit trail.