---
name: 03-subagents
description: Define scoped subagents in .claude/agents/ so recurring jobs like verification, simplification, and research each run in their own context window. Use when one session keeps re-reading the same material or when a check should be independent of the code that wrote it.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Edit
  - Bash(git status:*)
  - Bash(git add:*)
  - Bash(git commit:*)
metadata:
  stage: "03-build"
  persona: "engineer, tech-lead, platform"
  requires: "03-claude-md"
  produces: ".claude/agents/"
  indicators: "first-pass-implementation, changes-per-engineer"
  mcp: ""
  maturity: "beta"
---

# Subagents

## Job

Turn the jobs a session keeps redoing into named subagents with their own context
window, their own tool allowlist, and a prompt that says what "done" means.

A subagent is not a smaller model. It is a scope: a fresh context that reads only
what its job needs, reports a result, and leaves the main session's context
intact. Two things make one worth defining — the job recurs, or the job needs to
be done by something that did not write the code.

## Who uses this

- **Engineers** whose sessions run out of room re-reading the same files.
- **Tech leads** who want verification done by something with no stake in the
  change passing.
- **Platform engineers** standardizing the helpers every repo should have.

## Example prompts

- "Turn our verification checklist into a `verifier` subagent."
- "The main session keeps losing context tracing call paths. Give me a researcher subagent."
- "Review `.claude/agents/` — which of these should not be separate agents?"

## Steps

1. **Find the recurring job.** Read the last few sessions or PR threads. A job
   qualifies when it happened at least three times, has a stable definition of
   done, and produces a short answer from a lot of reading.
2. **Decide whether it needs independence.** Verification and review must be
   independent: the agent that wrote the code will find its own work correct.
   Research and simplification do not need independence — they need context room.
3. **Write the definition** to `.claude/agents/<name>.md`. Start from the
   templates in `templates/agents/` — `verifier.md`, `simplifier.md`,
   `researcher.md`, `spec-auditor.md` — rather than an empty file.
4. **Scope the tools.** List the fewest tools the job needs. A verifier that can
   `Edit` will eventually fix what it was asked to check, and the check becomes
   worthless. `references/agent-patterns.md` gives the tool sets that work.
5. **State the output contract.** The last line of the prompt should say exactly
   what the subagent returns and, where it matters, what it must never claim
   without evidence. "Never write VERIFIED from inference — only from output you
   ran" is the difference between a check and a formality.
6. **Wire it into the loop.** Name the subagent in the plan's **Proof** section
   and in `REVIEW.md`, so it is invoked by the process rather than remembered.
7. **Commit the definition.** Subagents steer the agent, so they go through the
   same PR review as code and belong in the eval suite (`04-continuous-evals`).

## What not to make a subagent

- A one-off question. The cost of the extra context window is not repaid.
- A job that needs the main session's state. A subagent starts fresh; if you
  have to paste half the conversation into it, keep the work inline.
- Anything with an irreversible side effect. Subagents propose; the session and
  its hooks decide.

## Output

- One or more `.claude/agents/<name>.md` definitions, each with a tool allowlist
  and an explicit output contract.
- References to them from `03-plan.md` **Proof** and `REVIEW.md`, so they run as
  part of the process.
- A note in `CLAUDE.md` naming which subagent to use for which job.

## Measure

| Indicator | Type | Where it comes from |
|---|---|---|
| `first-pass-implementation` | leading | an external system |
| `changes-per-engineer` | lagging | an external system |

Neither is computable from this repository. The signal to watch is simpler: if a
subagent's verdict is routinely overridden, its prompt is wrong or its scope is
too wide. Delete it rather than leaving a check nobody believes.

See `references/metrics-catalog.md` for the full indicator set.
