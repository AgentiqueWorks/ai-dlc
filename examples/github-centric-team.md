# GitHub-centric fully immersed AI team

In this model the GitHub repo is the single source of truth for backlog, agent memory, and the artifact chain. Every team member runs their own local agent (Claude Code, Codex, or Copilot) against the same repo.

## Principles

1. **Backlog lives in `intents/`**, not in a separate tool.
2. **Agent memory lives in `CLAUDE.md`, `AGENTS.md`, and `skills/`**, also in the repo.
3. **One branch per intent** carries the full artifact chain.
4. **Humans approve at the gates**; agents produce the artifacts.
5. **GitHub is the record**: branches, commits, PRs, and code reviews are the audit trail.

## Repo layout for the team

```
.
├── .claude/skills/          # skills from this package
├── .claude/hooks/           # governance hooks
├── CLAUDE.md                # project context every agent reads
├── AGENTS.md                # cross-client agent instructions
├── intents/                 # the backlog
│   ├── csv-export-20260826/
│   │   ├── 01-intent.md
│   │   ├── 02-spec.md
│   │   ├── 03-plan.md
│   │   ├── 04-review.md
│   │   ├── 05-deploy.md
│   │   └── 06-lessons.md
│   └── payment-audit-20260827/
│       └── 01-intent.md
├── src/                     # the actual code
├── tests/
└── .github/workflows/
```

## Branching convention

```
main
  └── intent/csv-export-20260826
```

A single branch per intent keeps the startup lean. The branch accumulates the numbered artifacts in `intents/<id>/` plus the code changes. One PR is opened. A human merges it when the full chain is accepted.

## Daily flow

### 1. PM creates the intent

```text
/01-intent-capture
```

The agent:

- Creates branch `intent/csv-export-20260826` from `main`.
- Writes `intents/csv-export-20260826/01-intent.md` from the template.
- Opens a draft PR.
- The PM reviews and approves the intent in the PR.

### 2. PM and designer write the spec

```text
/02-spec-writer
```

The agent reads `01-intent.md`, pulls the Figma mock, and writes `02-spec.md` in the same intent folder. The PM updates the PR review and resolves any concerns.

### 3. Engineer plans and builds

```text
/03-plan-mode
```

The agent writes `03-plan.md` and then implements the code on the same branch. `04-feedback-loop` runs tests and screenshots before the engineer calls it done.

### 4. PR review

```text
/05-pr-review
```

The agent loads `04-review.md`, the diff, and the spec/plan. It tags findings. The tech lead adds a human review, then merges to `main`.

### 5. Deploy and maintain

After merge, `06-closing-the-loop` watches Datadog/Sentry. Any anomaly writes a new `intents/<id>/01-intent.md` and starts the loop again.

## Backlog as a repo view

To see what is open, the agent can:

```text
List all intent files where status is not "done".
```

Or the team runs:

```bash
ai-dlc backlog
```

## Governance

- `.claude/hooks/` blocks production deploys without `RELEASE_APPROVAL`.
- `.claude/settings.json` denies `WebFetch`, `curl`, and reading `.env*`.
- Branch protection on `main` requires one human approval.

## Example intent folders

See `examples/intents/csv-export-20260826/` and `examples/intents/payment-audit-20260827/`.