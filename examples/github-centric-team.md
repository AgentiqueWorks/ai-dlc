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

The agent loads the diff, `REVIEW.md`, `02-spec.md`, and `03-plan.md`, runs the bug, security, and compliance passes, and writes its findings to `04-review.md`. It cannot approve or merge — `no-self-approve.sh` blocks that, and branch protection requires a human. The tech lead reviews the findings and merges to `main`.

### 5. Deploy

```text
/05-release-gate
```

`production-gate.sh` blocks the deploy until a release manager sets
`RELEASE_APPROVAL`. The authorization, the rollout steps, and the rollback
trigger are recorded in `05-deploy.md` — the record, never the token value.

### 6. Maintain and close the loop

After deploy, `06-closing-the-loop` watches Datadog and Sentry against
`bands.yaml`. Detection is deterministic: `detect-bands.sh` computes the
statistic and decides the tier, and only a 3-sigma breach invokes an agent, with
the tools that tier allows. A finding writes `06-lessons.md` — naming the file
that changed, a skill, a hook, or an eval — and a new
`intents/<new-id>/01-intent.md`, which starts the loop again.

## Backlog as a repo view

The repository is the backlog, so reading it is a command rather than a query:

```bash
ai-dlc backlog --wide
```

```
ID                      TITLE          STAGE    STATUS     CHAIN   NEXT          AGE
csv-export-20260826     CSV export     04-test  in-review  ●●●●○○  05-deploy.md   2d
payment-audit-20260827  Payment audit  01-plan  draft      ●○○○○○  02-spec.md    34d  stale
```

It reads intents that exist only on unmerged branches, so the whole queue is
visible from `main` — which is the point of the one-branch-per-intent
convention. Filter with `--stage 03`, `--status in-review`, or `--all` to include
finished work.

## Measuring the loop

```bash
ai-dlc metrics
```

Eight indicators come from the `intents/` tree and git history alone. The one to
read first is `plan-diff-alignment`: it compares `## Files that change` in
`03-plan.md` against the real diff on `intent/<id>`, which is the best local
signal for scope creep. `ai-dlc adoption` shows which play to add next.

## Governance

- `.claude/hooks/` blocks production deploys without `RELEASE_APPROVAL`.
- `.claude/settings.json` denies `curl`, `wget`, and reading `.env*` and
  `secrets/**`, and enables the sandbox with a network allowlist.
- `no-self-approve.sh` stops the agent approving or merging its own work.
- Branch protection on `main` requires one human approval.

## Example intent folders

See `examples/intents/csv-export-20260826/` and `examples/intents/payment-audit-20260827/`.