# Review instructions

## Passes

Run these passes and tag each finding:

- **Bugs:** logic errors, broken edge cases, subtle regressions.
- **Security:** injection risks, authentication gaps, PII in logs.
- **Compliance:** the change matches `spec.md`, `plan.md`, and design principles.

## Severity

- **Important:** would break behavior, leak data, or breach a policy.
- **Nit:** style, naming, formatting.

## Cap the nits

Report at most five nits; summarize the rest as a count.

## Do not report

Generated files and anything CI already enforces.