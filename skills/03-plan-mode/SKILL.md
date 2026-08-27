---
name: 03-plan-mode
description: Produce an implementation plan.md from an approved spec.md before any code is changed. Use at the start of the Build stage.
---

# Plan mode

## Job

Create a written implementation plan that names files, ordering, risks, and proof before any code is generated.

## Who uses this

- **Engineers** who want to think through a change before the agent writes code.
- **Tech leads** who need a plan they can review and approve.
- **QA** who want to see the proof the engineer will use before approving.

## Example prompts

- "Read `spec.md` for the CSV export and produce a `plan.md` before writing code."
- "What files change for the audit-logging feature? What is the riskiest step?"
- "Interrogate the plan: what could break, and what other options did you rule out?"

## Steps

1. Enter plan mode (or act as if in one): read the codebase, `CLAUDE.md`, and the approved `intents/<id>/02-spec.md`. Do not edit files yet.
2. Read the relevant code paths with `Read` and `Grep`.
3. If a GitHub issue or GitLab MR exists, use the `github` or `gitlab` MCP to fetch related context.
4. Write `intents/<id>/03-plan.md` using `templates/plan.md`:
   - files that change
   - order of work
   - risks and mitigations
   - proof (tests, screenshots, commands)
5. Ask the engineer to review: can someone who has not seen the conversation implement this from the plan alone?
6. Commit the approved `03-plan.md` on the same `intent/<id>` branch.
7. Only then implement. If the implementation departs from the plan, update `03-plan.md` in the same commit.

## Output

- `intents/<id>/03-plan.md` that is the audit checkpoint for the eventual PR.
- A risk register and a quantified proof checklist.