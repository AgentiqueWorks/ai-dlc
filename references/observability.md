# Observing the agent itself

The artifact chain records what was decided. Telemetry records what the agent did
to get there — how long gates held work up, how many sessions ran at once, which
hooks fired. Several indicators in the catalog have no other source.

## Turning it on

Claude Code exports metrics and logs over OpenTelemetry. The settings in
`governance/managed-settings.json` enable it for everyone:

```json
{
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp",
    "OTEL_LOGS_EXPORTER": "otlp",
    "OTEL_EXPORTER_OTLP_PROTOCOL": "http/protobuf",
    "OTEL_EXPORTER_OTLP_ENDPOINT": "https://otel-collector.internal:4318"
  }
}
```

Put it in managed settings rather than project settings. Telemetry that each
project opts into produces a dataset with a survivorship bias built in.

## What to build from it

| Indicator | Built from |
|---|---|
| `hook-wait-time` | Time between a tool call and its hook decision, per gate |
| `concurrent-sessions` | Distinct sessions active per engineer per hour |
| `gate-violations` | Blocked calls, by hook, compared before and after a gate ships |

`hook-wait-time` is the one that decides whether your governance survives
contact with a deadline. A gate that adds thirty seconds to every command is a
gate somebody will find a way around, and you will not hear about it.

## The local audit log

Independently of OpenTelemetry, `governance/hooks/_lib.sh` appends every gate
decision to `.ai-dlc/audit.jsonl`:

```json
{"at":"2026-08-27T09:14:02Z","hook":"production-gate.sh","tool":"Bash","decision":"deny","reason":"production deploy without a release authorization"}
```

This works with no collector, no vendor, and no configuration. For many teams it
is enough: combined with the committed artifact chain and the PR thread, it is
the record of who asked for what, what the agent produced, and who approved it.

Ship it to your log store if you need retention. Do not add it to `.gitignore`
and then cite it as your audit trail.

## What telemetry does not tell you

It measures activity, not value. Sessions, tokens, and tool calls all rise when
things are going badly. Every number here is read against a delivery indicator
from `metrics-catalog.md` — concurrency against review time, hook wait against
gate violations — or it is a vanity metric with a collector attached.
