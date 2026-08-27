# <Project name>

<!--
Keep this under a page. It is read at the start of every session, so every line
costs context. Long material belongs in `references/` and gets linked, not
inlined. When an agent makes the same mistake twice, that is a line for the
"Things Claude gets wrong" section — not a comment in the PR.
-->

## Commands

- **Build:** <command>
- **Test:** <command>
- **Lint:** <command>
- **Run one test:** <command>

## The loop

Work enters as an intent under `intents/<id>/` and moves through a committed
artifact chain: `01-intent.md` → `02-spec.md` → `03-plan.md` → code + tests →
`04-review.md` → `05-deploy.md` → `06-lessons.md`. One branch per intent
(`intent/<id>`), one PR, a human merges.

## Conventions

- <convention 1>
- <convention 2>

## Architecture

- <high-level layout: where the entry points, the domain logic, and the
  boundaries live>

## Frozen paths

Do not edit these without a human in the loop; hooks enforce it.

- `<path>` — <why>

## Things Claude gets wrong

- <common mistake 1>
- <common mistake 2>
