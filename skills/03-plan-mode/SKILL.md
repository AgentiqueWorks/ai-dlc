---
name: 03-plan-mode
description: Produce an implementation plan.md from an approved spec.md before any code is changed. Use at the start of the Build stage.
---

# Plan mode

## Job

Create a written implementation plan that names files, ordering, risks, and proof before any code is generated.

## Steps

1. Enter plan mode (or act as if in one): read the codebase and the approved `spec.md`, but do not edit files yet.
2. Ask the engineer what could break, which step is most risky, and what other options exist.
3. Produce `plan.md` using `templates/plan.md`: files that change, order of work, risks, and proof.
4. Iterate until someone who has not seen the conversation could implement the change from the plan.
5. Commit the approved `plan.md`.
6. Implement only after the plan is accepted. If implementation departs from the plan, update `plan.md` in the same commit.

## Output

- `plan.md` that serves as an audit checkpoint for the eventual PR.