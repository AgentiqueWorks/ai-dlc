---
name: 06-security-scan
description: Run scheduled security scans, validate findings, and route bounded fixes through the PR review gate or wider issues through a new intent.md. Use in the Maintain stage.
---

# Security scan

## Job

Scan a repository on a schedule and feed every finding through the normal SDLC gates.

## Who uses this

- **Security engineers** who want continuous, model-driven scans.
- **Engineering leads** tracking vulnerability trends.
- **SREs** adding an eval for a new incident class.

## Example prompts

- "Scan this repo for API security issues and open a PR for any bounded fix."
- "A new dependency vulnerability was found. Write an `intent.md` and start the loop."
- "Add this finding class to the eval suite."

## Steps

1. Run the configured scan (static analyzer, dependency checker, or model-driven scan).
2. Validate and rate each finding with confidence.
3. Use `github` or `gitlab` MCP to create a PR for bounded fixes.
4. For systemic issues, write an `intent.md` and start at Stage 1.
5. Add an eval for each vulnerability class once the fix ships.
6. Export or sync findings to the organization's existing tracker (Jira, ServiceNow, GitHub).

## Output

- Scan report with confidence ratings.
- PRs for bounded fixes or `intent.md` for systemic issues.
- Updated eval suite.