---
name: 06-security-scan
description: Run scheduled security scans, validate findings, and route bounded fixes through the PR review gate or wider issues through a new intent.md. Use in the Maintain stage.
---

# Security scan

## Job

Scan a repository on a schedule and feed every finding through the normal SDLC gates.

## Steps

1. Run the configured scan (a static analyzer, dependency check, or model-driven scan) against the repo.
2. Validate and rate each finding with confidence.
3. For a bounded fix, open a PR with the patch and route it through the review gate.
4. For a systemic or architectural issue, write an `intent.md` and start at Stage 1.
5. Add an eval for each vulnerability class once the fix ships.
6. Export or sync findings to the organization's existing tracker and audit systems.

## Output

- Scan report with confidence ratings.
- PRs for bounded fixes, `intent.md` for systemic issues.