---
name: 03-org-skills
description: Encode an organization's security, API, brand, and UX policies as version-controlled skills so the agent applies them during Design and Build instead of a reviewer catching them afterwards. Use when the same policy keeps showing up as a review finding.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Edit
  - Bash(git status:*)
  - Bash(git add:*)
  - Bash(git commit:*)
  - Bash(gh pr create:*)
metadata:
  stage: "03-build"
  persona: "policy-owner, security, designer, tech-lead"
  requires: ""
  produces: "skills/"
  indicators: "skill-merge-time, policy-cite-findings"
  mcp: "notion, confluence"
  maturity: "beta"
---

# Organization policy skills

## Job

Take a policy that currently lives in a wiki, a reviewer's head, or a recurring
PR comment, and make it something the agent applies while it works.

`02-spec-writer` and `05-pr-review` both say "apply the org skills that apply".
This is the play that creates them.

## Prerequisite

None. `CLAUDE.md` is strongly recommended first — a policy skill lands better
when the agent already knows how the repository works — but this play does not
depend on it, and a policy that keeps costing you review time is worth encoding
today.

## Who uses this

- **Policy owners** — security lead, API lead, design lead — who own the rule.
- **Tech leads** who keep leaving the same review comment.
- **Designers** whose brand and UX patterns are re-litigated every sprint.

## The test for a good policy skill

A rule an agent cannot check is not a rule. Write each one so a reviewer can
point at a line of code and say yes or no.

| Not a rule | A rule |
|---|---|
| "Follow security best practices" | "Never log a field named `ssn`, `email`, `phone`, or `name`" |
| "APIs should be consistent" | "List endpoints return `{data, cursor}`; never a bare array" |
| "Use the brand voice" | "Error messages state what happened and the next action; never apologize" |
| "Make it accessible" | "Every interactive element has a visible focus state and a 44px touch target" |

## Example prompts

- "Turn our PCI logging rules into a security skill."
- "The last six PRs all got the same pagination comment. Make it a skill."
- "Review our security skill — which rules can an agent not actually check?"

## Steps

1. **Find the policy that is costing you.** Read the last month of review
   findings. A policy cited three or more times is a policy that should have been
   applied during Build. `policy-cite-findings` is exactly this count.
2. **Get the source of truth.** Pull the real policy from Notion, Confluence, or
   wherever it lives — over MCP if it is connected. Do not write policy from
   memory; that produces a skill that disagrees with the wiki, and now you have
   two policies.
3. **Start from `templates/skills/`.** The `security/`, `api-design/`, `brand/`,
   and `ux-patterns/` directories there have the structure: rules, exceptions,
   steps, output.
4. **Write each rule in three parts:** what it is, what a violation looks like,
   and what to do instead. The violation example is what makes it checkable.
5. **Name the owner in the frontmatter** and record the review date. A policy
   skill with no owner rots into folklore with better formatting.
6. **Record exceptions with an expiry.** An exception without an owner and a date
   is an omission pretending to be a decision.
7. **Add an eval per rule.** `04-continuous-evals` — a real task that violates the
   rule, and a check that asserts the agent caught it. Without this you will not
   know when a model or skill change stops applying the policy.
8. **Ship it through PR review with the policy owner as required reviewer.** Add
   a `CODEOWNERS` entry for the skill's path so this is enforced, not remembered.

## Steps for keeping it honest

- Re-read the skill whenever the underlying policy changes; the skill is a copy,
  and copies drift.
- Delete rules that never fire. A skill full of dead rules dilutes the ones that
  matter.
- When a rule keeps producing false positives, the rule is wrong, not the agent.

## Output

- One skill directory per policy area under `skills/` (installed to
  `.claude/skills/`), each with an owner, a review date, and checkable rules.
- A `CODEOWNERS` entry routing changes to the policy owner.
- An eval per rule in `evals/`.

## Measure

| Indicator | Type | Where it comes from |
|---|---|---|
| `policy-cite-findings` | lagging | an external system |
| `skill-merge-time` | leading | an external system |

`policy-cite-findings` should fall toward zero once the skill applies the policy
during Build. If it does not, the rule is not written in a form the agent can
act on. `skill-merge-time` measures whether policy can actually move: a skill
that takes three weeks to merge is a policy nobody will keep current.

See `references/metrics-catalog.md` for the full indicator set.
