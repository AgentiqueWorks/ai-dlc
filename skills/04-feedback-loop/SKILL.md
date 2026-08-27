---
name: 04-feedback-loop
description: Verify an agent's work before reporting it done using build, test, lint, and visual checks. Use during implementation in the Build and Test stages.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Edit
  - Bash(make:*)
  - Bash(npm test:*)
  - Bash(npm run:*)
  - Bash(pytest:*)
  - Bash(cargo test:*)
  - Bash(go test:*)
  - mcp__playwright__browser_navigate
  - mcp__playwright__browser_take_screenshot
metadata:
  stage: "04-test"
  persona: "engineer, qa"
  requires: "03-claude-md"
  produces: ""
  indicators: "ci-first-pass-rate"
  mcp: "playwright, github"
  maturity: "stable"
---

# Feedback loop

## Job

Make the agent prove its work before a human reviews it.

## Who uses this

- **Engineers** who want the agent to self-check before calling them back.
- **QA / Test engineers** who define the proof criteria.
- **Tech leads** who want green checks before they review the diff.

## Example prompts

- "Run the tests and build before saying this is done."
- "Open the app, take a screenshot of the CSV export button, and compare it to the Figma mock."
- "Do not edit the test file to make the test pass."

## Steps

1. Read the `CLAUDE.md` commands for build, test, lint, and verification.
2. Run each command and inspect the output.
3. If a command fails, fix the code, not the test or the check.
4. For UI work, use Playwright or the client's browser tool:
   - `browser_navigate` to the page
   - `browser_screenshot` to capture the result
   - compare to the Figma or approved mock
5. Paste the evidence (command output or screenshot summary) into the session.
6. Do not mark the task complete until the quantified proof passes.

## Output

- Pasted build/test/lint output or screenshot evidence.
- A green check and a summary of what was verified.

## Measure

| Indicator | Type | Where it comes from |
|---|---|---|
| `ci-first-pass-rate` | leading | an external system |

This is the play that moves `ci-first-pass-rate`. If it is not moving, the session is claiming done without running the commands.

See `references/metrics-catalog.md` for the full indicator set.
