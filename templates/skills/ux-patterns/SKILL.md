---
name: ux-patterns
description: <One line naming the policy and when it applies. Example: Apply the organization's UX pattern policy to any change that touches <area>. Use during Design, Build, and Review.>
metadata:
  owner: "Design lead"
  applies_to: "02-design, 03-build, 05-deploy"
  reviewed: "<YYYY-MM-DD>"
---

# UX pattern policy

<!--
This is a template. Replace every placeholder with your actual policy. A rule an
agent cannot check is not a rule — write each one so a reviewer can point at a
line of code and say yes or no.
-->

## Job

Constrain any change that touches <area> so it complies with the organization's
UX pattern policy without a human having to remember the rules.

## Who owns this

**Design lead.** Changes to this file require their approval. Record the date of the
last policy review in the frontmatter.

## Rules

Each rule is stated so that it can be checked against a diff.

1. **<Rule name>.** <The rule, stated concretely.>
   - Applies when: <the condition>
   - Violation looks like: <a concrete example>
   - Do this instead: <the compliant form>

2. **<Rule name>.** <...>

## Exceptions

An exception is a decision, not an omission. Record it here with an owner and an
expiry, or it does not exist.

| Exception | Granted by | Expires | Reason |
|---|---|---|---|
| <what> | <who> | <YYYY-MM-DD> | <why> |

## Steps

1. Read the change and decide whether any rule above applies. If none does, say
   so and stop.
2. For each applicable rule, check the change against it and cite the file and
   line.
3. Report violations as findings in `intents/<id>/04-review.md` with the rule
   number, never as a general observation.
4. If a rule is ambiguous for this change, do not guess: flag it in the spec's
   **Areas of concern** table and route it to Design lead.

## Output

- A per-rule verdict with citations.
- Findings routed to the review artifact.
- Anything ambiguous routed to Design lead rather than resolved by the agent.
