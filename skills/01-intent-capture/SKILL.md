---
name: 01-intent-capture
description: Capture an idea, ticket, or alert as a human-readable and machine-actionable intent.md. Use for new ideas, Jira/GitHub/Monday tickets, or incidents.
---

# Intent capture

## Job

Turn a vague idea or an incoming signal into a committed `intent.md` using the repository template. This is the entry point to the SDLC loop.

## Who uses this

- **Product managers** who receive feedback from Slack, Intercom, Zendesk, or customer calls.
- **SREs / on-call engineers** responding to an incident or a breached control band.
- **Engineers** who notice a problem and want to write it up before fixing it.

## Example prompts

- "A customer reported they cannot export to CSV. Turn this Intercom thread into an `intent.md`."
- "Production 5xx rate is spiking. Write an `intent.md` for the on-call queue."
- "JIRA-4822 asks for audit logging. Capture it as an `intent.md` and list the constraints."

## Steps

1. Identify the source: an idea, a Slack thread, an Intercom/Zendesk ticket, a Jira/Linear/Monday item, an incident, or a metric alert.
2. If a source system is available, use the relevant MCP tool to pull the title and body:
   - Slack: `get_thread` or `conversations_replies`
   - Intercom: `list_conversations` / `get_conversation`
   - Jira: `get_issue`
   - Linear: `get_issue`
   - Monday: `get_items`
   - Datadog: `query_metrics` (for alerts)
3. Ask the originator the five questions: what is the problem, who is affected, what does better look like, what constraints apply, and what is out of scope.
4. Draft `intent.md` using `templates/intent.md`.
5. Surface any contradictions or missing constraints.
6. Propose a source link and a record ID (e.g. `intent/JIRA-4822.md`).
7. Stage the file; do not commit without human approval.

## Output

- `intent.md` with a clear problem, proposed outcome, affected users/systems, constraints, and open questions.
- A link back to the source ticket, thread, or alert.
- A recommendation on whether the item is ready for design.