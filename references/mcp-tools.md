# MCP tool names by action

Tool names are chosen by each server and change between versions. Treat this as a
map of *where to look*, not as an API contract — and never hard-code an MCP tool
name into a skill's `allowed-tools`, because the server name is chosen by
whoever installed it.

| You need to | Server | Tools usually named |
|---|---|---|
| Read a support thread | `intercom` | `search_conversations`, `get_conversation` |
| Read a chat thread | `slack` | `search_messages`, `get_thread`, `post_message` |
| Read or write a ticket | `jira`, `linear`, `monday` | `get_issue`, `search_issues`, `create_issue`, `add_comment` |
| Read a design | `figma` | `get_file`, `get_node`, `export_image` |
| Read a document | `notion`, `confluence`, `google-workspace` | `search`, `get_page`, `get_document` |
| Read code and PRs | `github`, `gitlab` | `get_pull_request`, `list_files`, `create_pull_request`, `get_workflow_run` |
| Query a metric | `datadog` | `query_metrics`, `list_monitors`, `get_events` |
| Read an error | `sentry` | `list_issues`, `get_issue`, `get_event` |
| Page or acknowledge | `pagerduty` | `list_incidents`, `acknowledge_incident` |
| Check a deployment | `vercel` | `list_deployments`, `get_deployment` |
| Drive a browser | `playwright` | `browser_navigate`, `browser_take_screenshot`, `browser_click` |
| Read payment data | `stripe` | `list_charges`, `get_customer` |

## Fragment format

One server per file in `mcp/configs/<name>.json`, with the filename matching the
server key:

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp",
      "headers": { "Authorization": "Bearer ${GITHUB_TOKEN}" }
    }
  }
}
```

`type` is `stdio`, `http`, or `sse`. Every credential is a `${VAR}` placeholder;
`ai-dlc validate` rejects literal values and scans for real tokens.

Run `ai-dlc mcp-sync` after editing. It regenerates `mcp.json`,
`claude-mcp.json` (`mcpServers`), `copilot-mcp.json` (`servers`), and
`codex-mcp.toml` (`[mcp_servers.*]`). Validation fails if those drift.
