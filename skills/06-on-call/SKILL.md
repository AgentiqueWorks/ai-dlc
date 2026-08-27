---
name: 06-on-call
description: Triage incidents arriving via Slack, Jira, or other channels, verify metrics over MCP, and write post-mortems or PRs. Use for first-response and on-call automation.
---

# On-call

## Job

Be a first responder to incidents that arrive through workplace communication tools.

## Who uses this

- **SREs** doing first response.
- **Engineers** who are on-call.
- **Incident commanders** who need status updates and post-mortems.

## Example prompts

- "PagerDuty just fired PD-2026. Ack it and tell me what is broken."
- "A customer posted in Slack #incidents that checkout is failing. Triage."
- "Write the post-mortem for this incident to `lessons/incident-42.md`."

## Steps

1. Read the incident from the triggering channel or ticket using the Slack, Jira, or PagerDuty MCP server.
2. Acknowledge the incident in the same channel or ticket.
3. Investigate: read logs, recent GitHub/GitLab commits or deployments, and relevant Datadog metrics.
4. Verify the metric is back at baseline.
5. If the fix is small and bounded, open a PR through the review gate.
6. If the fix is larger, write `intent.md` and start the SDLC loop.
7. Write a post-mortem to a version-controlled `lessons/<incident-id>.md`.

## Output

- Acknowledgement and status updates in the source channel/ticket.
- A PR or `intent.md`.
- A post-mortem.