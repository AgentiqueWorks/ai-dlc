---
name: 02-spec-writer
description: Turn an accepted intent.md into a requirements and design spec.md, applying organizational skills and flagging areas of concern. Use at the Design stage.
---

# Spec writer

## Job

Read an accepted `intent.md` and produce a requirements and design `spec.md` ready for engineering.

## Steps

1. Load the accepted `intent.md` and any organizational skills the user has available (brand, security, compliance, UX).
2. Conduct a design session: ask clarifying questions if needed, then draft requirements, design, acceptance criteria, and out-of-scope items.
3. Flag any areas of concern where constraints conflict or where the design cannot satisfy a policy.
4. Write `spec.md` using `templates/spec.md`.
5. Resolve each flagged concern with the appropriate policy owner before moving to Build.

## Output

- `spec.md` placed next to the source `intent.md`.
- A list of resolved or carried-forward concerns.
- A recommendation on whether the spec is ready for the plan-mode step.