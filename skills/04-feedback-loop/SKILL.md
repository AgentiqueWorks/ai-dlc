---
name: 04-feedback-loop
description: Verify an agent's work before reporting it done using build, test, lint, and visual checks. Use during implementation in the Build and Test stages.
---

# Feedback loop

## Job

Make the agent prove its work before a human reviews it.

## Steps

1. Read the `CLAUDE.md` commands for build, test, and lint.
2. Run the relevant commands and inspect the output.
3. If any command fails, fix the code, not the test or the check.
4. For UI work, use a browser or screenshot tool to compare the result with the approved mock.
5. Paste the evidence into the session.
6. Do not mark the task complete until the quantified proof passes.

## Output

- Pasted build/test/lint output or screenshot evidence.
- A green check before the human sees the diff.