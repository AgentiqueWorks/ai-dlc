# MCP catalog for the AI-Native SDLC

This catalog maps common SDLC actions to the MCP servers and tool names a team is likely to use. Tool names vary by host and version; always call `list_tools` if the client exposes it.

## Legend

- **Action** — the thing the agent wants to do.
- **Server** — the MCP server alias to use.
- **Likely tool names** — common tool identifiers; the actual names may differ.
- **Used by** — which skill or persona typically needs this.

## Plan and design

| Action | Server | Likely tool names | Used by |
|---|---|---|---|
| Read a Slack thread | slack | `conversations_replies`, `get_thread`, `chat_postMessage` | `01-intent-capture`, `06-on-call` |
| Read a customer support ticket | intercom | `list_conversations`, `get_conversation` | `01-intent-capture` |
| Read product docs/PRD | notion | `retrieve-page-markdown`, `search` | `01-intent-capture`, `02-spec-writer` |
| Read a Confluence page | confluence | `get_page`, `search_pages` | `01-intent-capture`, `02-spec-writer` |
| Read a Google Doc | google-workspace | `get_document`, `search_drive` | `01-intent-capture`, `02-spec-writer` |
| Find a Jira ticket | jira | `get_issue`, `search_issues` | `01-intent-capture`, `02-spec-writer` |
| Find a Linear issue | linear | `get_issue`, `search_issues` | `01-intent-capture`, `02-spec-writer` |
| Find a Monday item | monday | `get_items`, `get_boards` | `01-intent-capture`, `02-spec-writer` |
| Query a Figma file | figma | `get_file`, `get_node` | `02-spec-writer` |
| Create a Figma comment | figma | `post_comment` | `02-spec-writer` |

## Build and track

| Action | Server | Likely tool names | Used by |
|---|---|---|---|
| Find a GitHub issue/PR | github | `search_issues`, `get_pull_request` | `01-intent-capture`, `03-plan-mode` |
| Find a GitLab MR | gitlab | `get_merge_request`, `list_issues` | `01-intent-capture`, `03-plan-mode` |
| Create a GitHub issue | github | `create_issue` | `06-closing-the-loop` |
| Create a GitLab MR | gitlab | `create_merge_request` | `05-pr-review` |
| Get repo file tree | github / gitlab | `get_repo_tree` / `get_project_tree` | `03-plan-mode` |
| Read file contents | github / gitlab | `get_file_contents` | `03-plan-mode` |

## Test and deploy

| Action | Server | Likely tool names | Used by |
|---|---|---|---|
| Take a screenshot or drive a browser | playwright | `browser_navigate`, `browser_screenshot` | `04-feedback-loop` |
| Run an existing E2E test | playwright | `browser_navigate` + local test runner | `04-feedback-loop` |
| List Vercel deployments | vercel | `list_deployments`, `get_deployment` | `05-release-gate` |
| Promote a Vercel deployment | vercel | `promote_deployment` | `05-release-gate` |
| Get build logs | github / vercel / gitlab | `get_workflow_run`, `get_deployment` | `05-cicd-triage` |

## Maintain and observe

| Action | Server | Likely tool names | Used by |
|---|---|---|---|
| Query a Datadog metric | datadog | `query_metrics`, `get_monitor` | `06-closing-the-loop` |
| List Sentry issues | sentry | `list_issues`, `get_issue` | `06-security-scan`, `06-on-call` |
| Get a PagerDuty incident | pagerduty | `get_incident`, `list_incidents` | `06-on-call` |
| Ack an incident | pagerduty | `acknowledge_incident` | `06-on-call` |
| Get customer feedback | intercom | `list_conversations`, `get_conversation` | `01-intent-capture` |

## Commerce and billing

| Action | Server | Likely tool names | Used by |
|---|---|---|---|
| Get a Stripe customer | stripe | `get_customer` | `01-intent-capture`, `06-closing-the-loop` |
| List recent charges/refunds | stripe | `list_charges` | `06-security-scan`, `06-on-call` |

## Notes

- Some servers listed use remote OAuth endpoints; others require an `npx` command. See the matching `mcp/configs/*.json` file.
- Tokens must be supplied by the user. Never commit them.
- If a tool name does not match, the skill should still work by asking the agent to discover the actual tool with `list_tools`.