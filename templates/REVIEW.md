# Review instructions

The agent reads this file before reviewing a pull request. It is policy, so it
changes through the same PR process as the code.

## Context to load first

- The diff.
- `intents/<id>/02-spec.md` — what was asked for.
- `intents/<id>/03-plan.md` — what was promised.
- `CLAUDE.md` — how this codebase works.
- The org policy skills that apply (security, api-design, brand, ux).

## Passes

Run these passes in order and tag every finding with its pass:

- **Bugs:** logic errors, broken edge cases, subtle regressions, unhandled
  failure paths, concurrency and ordering mistakes.
- **Security:** injection, authentication and authorization gaps, PII in logs,
  secrets in code, unsafe deserialization, missing input validation.
- **Compliance:** does the change match `02-spec.md` and `03-plan.md`? Name any
  file changed that the plan did not list, and any planned file left untouched.

## Severity

- **Blocking:** would break behavior, leak data, or breach a policy.
- **Important:** should be fixed before merge but is not a breach.
- **Nit:** style, naming, formatting.

## Cap the nits

Report at most five nits; summarize the rest as a count. A review that is mostly
nits will be skimmed, and the blocking finding will be missed.

## Do not report

- Generated files and lockfiles.
- Anything CI already enforces (formatting, lint rules, type checks). If CI
  catches it, CI should report it — a duplicate finding trains people to skim.
- Style preferences not written down in `CLAUDE.md` or a skill.

## Rules

- Every finding names a file and a line.
- Every finding states the failure: the input or state, and the wrong result.
- If you cannot state the failure, it is not a finding.
- The agent never approves the pull request. It writes
  `intents/<id>/04-review.md` and a human decides.
