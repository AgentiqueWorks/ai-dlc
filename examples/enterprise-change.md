# Enterprise change: payment audit logging

## Scenario

A regulated fintech needs to add audit logging to payment events. The change requires security review, a change ticket, and a release-authorization gate.

## Transcript

**PM in Jira**: `JIRA-4822` — "Add audit logging to payment events."

**PM**: `/01-intent-capture`  
Agent pulls `JIRA-4822` via the Jira MCP and writes `intent/payment-audit.md`, noting PCI and PII constraints.

**PM + Security**: `/02-spec-writer`  
Agent applies the security and compliance skills. It flags: "Audit events must include actor, action, entity, and timestamp; PII must not appear in logs." The security policy owner resolves the concern.

**Engineer + Security architect**: `/03-plan-mode`  
Agent writes `plan.md` with `payments/events.rs` and `audit/schema.sql` changes. The plan is routed for higher-risk sign-off.

**Engineer**: Implements. `.claude/hooks/` blocks edits to `schema.sql` without a change-ticket number. `04-feedback-loop` runs `make test` and `make lint`.

**QA**: `/04-continuous-evals`  
Agent adds an eval for the new audit-log schema and runs it in CI.

**Tech lead + Release manager**: `/05-pr-review` and `/05-release-gate`  
PR review runs bug/security/compliance passes. The release hook blocks the deploy until `RELEASE_APPROVAL` is set. The change-advisory board authorizes the release.

**SRE + Security**: `/06-closing-the-loop` and `/06-security-scan`  
Datadog monitors the new logs. Sentry watches for anomalies. Each finding flows back as a new `intent.md` or a PR.