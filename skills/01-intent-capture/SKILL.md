---
name: 01-intent-capture
description: Capture an idea, ticket, or alert as a human-readable and machine-actionable intent.md. Use for new ideas, Jira/GitHub/Monday tickets, or incidents.
---

# Intent capture

## Job

Turn a vague idea or incoming signal into a committed `intent.md` using the repository template.

## Steps

1. Ask the originator for the problem, affected users, proposed outcome, constraints, and open questions.
2. If an external ticket or message triggered this, use the relevant MCP tool (Jira/Slack/GitHub/Monday) to pull the source text and link the record ID.
3. Write the artifact to `intent.md` (or `intent/<record-id>.md`) using `templates/intent.md`.
4. Surface any contradictions or missing constraints before committing.
5. Stage the file; wait for the product owner to accept, merge, or close it.

## Output

- `intent.md` with a clear problem, proposed outcome, affected users/systems, constraints, and open questions.
- A link back to the source ticket or message if one exists.