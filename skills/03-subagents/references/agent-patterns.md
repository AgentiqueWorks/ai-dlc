# Subagent patterns

Four shapes cover most of what a team needs. Each is a scope decision first and a
prompt second.

## Verifier — independence

| | |
|---|---|
| Tools | `Read, Grep, Glob, Bash` |
| Never | `Write`, `Edit` |
| Returns | Per-check pass/fail with the actual output |

The point is that it cannot fix what it finds. A verifier with edit access will
make the test pass rather than report that it failed, and you will not notice
until production. Its prompt must forbid inferring success: a check is passed
only when the command was run and the output was read.

## Simplifier — a second pass with fresh eyes

| | |
|---|---|
| Tools | `Read, Grep, Glob` |
| Never | `Bash`, `Write`, `Edit` |
| Returns | Concrete removals, each with an existing replacement |

Runs after the change works. It needs a fresh context precisely because the main
session is attached to the code it just wrote. Tell it explicitly not to comment
on style — otherwise you get a linter with opinions.

## Researcher — context economy

| | |
|---|---|
| Tools | `Read, Grep, Glob` |
| Never | anything that writes |
| Returns | A call path as `file:line` hops, plus constraints |

This one exists to protect the main context window, not for independence. It
reads twenty files and returns fifteen lines. Require it to say "not determined"
rather than speculate; a researcher that guesses is worse than no researcher.

## Spec auditor — plan fidelity

| | |
|---|---|
| Tools | `Read, Grep, Glob, Bash(git diff:*)` |
| Never | `Write`, `Edit` |
| Returns | planned-and-changed / planned-but-untouched / changed-but-unplanned |

Mechanical comparison of `03-plan.md` against the diff. It computes the same
thing `ai-dlc metrics --indicator plan-diff-alignment` does, but inside a review
session where it can also judge whether the departure was reasonable.

## Tool scoping rules

1. Start from nothing and add what the job provably needs.
2. `Bash` is not one permission. `Bash(git diff:*)` and `Bash` are very different
   grants.
3. If a subagent needs `Write`, ask what it is for. Reporting is not writing.
4. MCP tool names depend on what the user named their server. Prefer describing
   the capability in the prompt over hard-coding `mcp__github__*`, which breaks
   for anyone whose server is named differently.

## When one agent should be two

Split when the two halves need different tool sets, or when one half must be
independent and the other must not. Do not split by topic alone — two agents that
read the same files and could share a context are one agent.
