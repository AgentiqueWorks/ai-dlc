# Lessons: CSV export for the reports table

- **From deploy:** `intents/csv-export-20260826/05-deploy.md`
- **Status:** done
- **Date:** 2026-08-27

## What the loop produced

- **Signal to intent:** 2h 10m (Intercom thread to committed `01-intent.md`)
- **Intent to merge:** 1d 6h
- **Plan fidelity:** departed once — `src/lib/csv.ts` was added during
  implementation and the plan was updated in the same commit, as the play
  requires.

## What went well

- The plan named the streaming approach before any code existed, so the
  memory-usage question was settled in review of the plan rather than in review
  of a 400-line diff.
- `04-feedback-loop` caught the missing `Content-Disposition` header from the
  Playwright screenshot, before a human opened the PR.

## What went wrong

- The review found missing input validation on the `columns` query parameter.
  Nothing in the agent's configuration said anything about validating
  user-supplied column lists, so there was no reason it would have.
- The first implementation buffered the whole export in memory. The spec said
  "large workspaces" without saying what large meant.

## Changes to the agent configuration

| Lesson | Where it now lives | PR |
|---|---|---|
| Validate user-supplied field and column lists against an allowlist | `skills/security/SKILL.md`, rule 4 | #412 |
| Export endpoints stream; they do not buffer | `CLAUDE.md`, Conventions | #413 |
| Regression: request 50k rows and assert constant memory | `evals/csv-export-streaming.json` | #413 |
| "Large" in a spec must carry a number | `templates/02-spec.md`, acceptance criteria note | #414 |

## Follow-up intents

- `intents/export-formats-20260901/01-intent.md` — the same customer asked for
  XLSX; the streaming work makes it cheap, so it re-entered the loop as its own
  intent rather than as scope creep on this one.
