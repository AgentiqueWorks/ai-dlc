---
name: 03-parallel-sessions
description: Run several agent sessions at once in separate git worktrees so independent tasks do not collide, and keep review quality from falling as parallelism rises. Use once CLAUDE.md, tests, and hooks are mature enough that a session can be trusted unattended.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(git worktree:*)
  - Bash(git status:*)
  - Bash(git switch:*)
  - Bash(git branch:*)
  - Bash(git log:*)
  - Write
  - Edit
metadata:
  stage: "03-build"
  persona: "engineer, tech-lead"
  requires: "03-claude-md, 04-feedback-loop"
  produces: ""
  indicators: "concurrent-sessions, changes-per-engineer"
  mcp: "github"
  maturity: "beta"
---

# Parallel sessions

## Job

Let one engineer supervise several agent sessions at once without the sessions
colliding on files, on branches, or on the engineer's attention.

## Who uses this

- **Engineers** with more independent work queued than one session can carry.
- **Tech leads** deciding whether the team is ready for this at all.

## Prerequisites — check before you start

Parallelism multiplies whatever your guardrails already do. If the guardrails are
weak, it multiplies the damage and the review burden. Do not start until:

- `CLAUDE.md` is accurate enough that a session gets the build and test commands
  right without help (`03-claude-md`).
- A session verifies its own work before reporting done (`04-feedback-loop`).
- Hooks block the operations you would not want happening unattended
  (`05-release-gate`).
- Tests are fast enough to run per session without contention.

## Example prompts

- "Set up worktrees for the three intents in this week's backlog."
- "Which of these queued intents can run in parallel without touching the same files?"
- "Clean up the worktrees for intents that have merged."

## Steps

1. **Pick tasks that are actually independent.** Read each intent's
   `03-plan.md` and compare the `## Files that change` lists. Overlapping lists
   mean the sessions will conflict; run those in sequence. This is the one step
   that decides whether parallelism helps or hurts.
2. **Give each task its own worktree**, so the sessions cannot see each other's
   uncommitted files:

   ```
   git worktree add ../<repo>-<intent-id> -b intent/<intent-id>
   ```

3. **Start one session per worktree**, each pointed at its own intent folder.
   Every session reads the same `CLAUDE.md` and skills; nothing is per-session
   configuration.
4. **Give each session a definition of done** from its plan's **Proof** section,
   so it stops at a reviewable point instead of waiting for you.
5. **Review serially even though the work ran in parallel.** The bottleneck moves
   to your attention, not the machine. If review quality drops, you are running
   too many; that is the signal, not the session count.
6. **Tear down when the branch merges:**

   ```
   git worktree remove ../<repo>-<intent-id>
   git worktree prune
   ```

7. **Keep one shared queue.** `ai-dlc backlog` shows which intents are in flight
   and at what stage, so a second engineer does not start a third session on the
   same intent.

## Failure modes

- **Shared ports and fixtures.** Two sessions running the dev server or the test
  database on the same port will fail in ways that look like code bugs. Give each
  worktree its own port range.
- **Long-lived worktrees.** A worktree that outlives its branch drifts from
  `main` and its session starts giving advice about code that has changed.
- **Parallelism as a throughput target.** The number to hold steady is review
  quality. Concurrency is an input, not a goal.

## Output

- One worktree and one branch per in-flight intent.
- A backlog view (`ai-dlc backlog`) that shows what is in flight and where.
- Cleaned-up worktrees once branches merge.

## Measure

| Indicator | Type | Where it comes from |
|---|---|---|
| `concurrent-sessions` | leading | an external system |
| `changes-per-engineer` | lagging | an external system |

Read both alongside `rework-after-review` from `ai-dlc metrics`. Throughput that
rises while rework rises is not throughput.

See `references/metrics-catalog.md` for the full indicator set.
