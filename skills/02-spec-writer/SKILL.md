---
name: 02-spec-writer
description: Turn an accepted intent.md into a requirements and design spec.md, applying organizational skills and flagging areas of concern. Use at the Design stage.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Edit
  - Bash(git status:*)
  - Bash(git diff:*)
  - Bash(git log:*)
  - Bash(git add:*)
  - Bash(git commit:*)
  - Bash(git switch:*)
metadata:
  stage: "02-design"
  persona: "product-owner, pm, designer, tech-lead"
  requires: "01-intent-capture"
  produces: "intents/<id>/02-spec.md"
  indicators: "stage-latency, spec-churn"
  mcp: "figma, notion, confluence, jira"
  maturity: "stable"
---

# Spec writer

## Job

Read an accepted `intent.md` and produce a requirements and design `spec.md` ready for engineering.

## Who uses this

- **Product managers** who need a spec they can hand to engineers.
- **Designers** who want the spec to reference Figma mocks and design-system rules.
- **Security / compliance leads** who need policy concerns flagged before build begins.

## Example prompts

- "Read `intent/JIRA-4822.md` and write `spec.md` for the audit-logging feature."
- "Pull the Figma mock for the CSV export and include the design in the spec."
- "Apply the security and brand skills and flag any conflicts."

## Steps

1. Load the accepted `intents/<id>/01-intent.md` and any relevant organizational skills (brand, security, compliance, UX, API standards).
2. If a Figma or design file is mentioned, use the `figma` MCP to pull the relevant frame or node.
3. If background documentation lives in Notion, Confluence, or Google Docs, use the matching MCP to read it.
4. Draft `intents/<id>/02-spec.md` using `templates/02-spec.md`:
   - requirements
   - design and data flow
   - acceptance criteria
   - explicit out-of-scope items
   - areas of concern
5. For each area of concern, identify the policy owner and route it for resolution.
6. Ask the PM or designer: does the spec solve the stated problem? Are open questions answered or carried forward?
7. Commit `02-spec.md` next to `01-intent.md` on the same `intent/<id>` branch only after the PM accepts.

## Output

- `intents/<id>/02-spec.md` that is ready for the plan-mode step.
- A list of resolved or carried-forward concerns and who resolved them.
- A go / no-go recommendation for Build.

## Measure

| Indicator | Type | Where it comes from |
|---|---|---|
| `stage-latency` | leading | `ai-dlc metrics` |
| `spec-churn` | lagging | `ai-dlc metrics` |

Rising `spec-churn` means requirements are still moving after the plan was committed — the spec advanced to Build too early.

See `references/metrics-catalog.md` for the full indicator set.
