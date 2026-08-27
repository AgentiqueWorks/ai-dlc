# MCP tool mapping for SDLC actions

## Generic SDLC action → MCP server

| Action | Preferred server | Likely tool names |
|---|---|---|
| Find an issue or PR | GitHub | `search_issues`, `get_issue`, `get_pull_request` |
| Create an issue | GitHub | `create_issue` |
| Comment on a PR | GitHub | `create_issue_comment` |
| Read a Jira ticket | Jira | `get_issue`, `search_issues` |
| Create a Jira ticket | Jira | `create_issue` |
| Update ticket status | Jira | `update_issue`, `transition_issue` |
| Post to a Slack channel | Slack | `post_message`, `chat_postMessage` |
| Read Slack thread | Slack | `conversations_replies`, `get_thread` |
| Query a Monday board | Monday | `get_boards`, `get_items` |
| Update a Monday item | Monday | `update_item`, `change_column_value` |

## Notes

- Server tool names vary by host and version. Use `list_tools` first if the agent exposes it.
- Tokens must be supplied by the user; this repo only ships URL skeletons.