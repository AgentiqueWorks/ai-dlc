---
name: 06-on-call
description: Triage incidents arriving via Slack, Jira, or other channels, verify metrics over MCP, and write post-mortems or PRs. Use for first-response and on-call automation.
---

# On-call

## Job

Be a first responder to incidents that arrive through workplace communication tools.

## Steps

1. Read the incident from the triggering channel or ticket using the Slack/Jira MCP server.
2. Acknowledge the incident in the same channel or ticket.
3. Investigate by reading logs, metrics, and recent commits. Use the GitHub MCP server to inspect recent diffs or PRs.
4. Verify the metric is back at baseline using the relevant monitoring MCP or Bash tool.
5. If the fix is small and bounded, open a PR through the review gate.
6. If the fix is larger, write `intent.md` and start the SDLC loop.
7. Write a post-mortem to a version-controlled `lessons.md` or incident record.

## Output

- Acknowledgement and status updates in the source channel/ticket.
- Either a PR or an `intent.md`, plus a post-mortem.