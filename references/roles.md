# Roles

The playbook keeps human judgement above the loop and gives agents the mechanical
work in between. That only holds if it is clear who decides what.

## Who decides what

| Role | Decides | Skills they drive | Cannot be an agent |
|---|---|---|---|
| **Originator** | That a problem is worth capturing | `01-intent-capture` | — |
| **Product owner** | Whether an intent advances to Design; whether a spec advances to Build | `01-intent-capture`, `02-spec-writer` | ✓ |
| **Policy owner** | What the organization's rules are | `03-org-skills` | ✓ |
| **Engineer** | Whether a plan is implementable; maintains `CLAUDE.md` | `03-plan-mode`, `03-claude-md`, `04-feedback-loop` | — |
| **Tech lead** | Review policy (`REVIEW.md`); higher-risk specs; the eval suite | `05-pr-review`, `04-continuous-evals` | ✓ |
| **Code owner** | Whether a pull request merges | `05-pr-review` | ✓ |
| **Security lead** | Security skills; which scan findings are real | `03-org-skills`, `06-security-scan` | ✓ |
| **QA** | What the eval suite must cover | `04-continuous-evals` | — |
| **Release manager** | Whether a change goes to production | `05-release-gate` | ✓ |
| **Platform engineer** | Where intents live; CI wiring; managed settings | `05-managed-settings`, `05-cicd-integration` | — |
| **Service owner** | Detection rules, control bands, rollback paths | `06-closing-the-loop` | ✓ |
| **On-call engineer** | Whether an incident fix ships now | `06-on-call` | — |

The last column is the load-bearing one. Where it is marked, the decision is a
judgement about intent, risk, or policy — and a gate exists specifically to stop
an agent making it: `no-self-approve.sh`, `production-gate.sh`,
`migration-ticket.sh`, and branch protection.

## Separation of duties

Three rules, each enforced by something deterministic rather than by convention:

1. **The agent that wrote the code cannot approve it.** `no-self-approve.sh`
   blocks `gh pr review --approve` and `gh pr merge`; branch protection requires a
   human code owner.
2. **The reviewer cannot authorize the release.** `production-gate.sh` needs
   `RELEASE_APPROVAL`, which the release manager sets.
3. **The policy owner signs off policy changes.** A `CODEOWNERS` entry on
   `skills/` routes every skill change to them.

## One artifact, one accountable human

Every artifact in the chain has a human who accepted it, recorded in the artifact
itself and in the commit that added it.

| Artifact | Accepted by | Recorded in |
|---|---|---|
| `01-intent.md` | Product owner | **Acceptance** section |
| `02-spec.md` | Product owner, plus policy owners for flagged concerns | **Go / no-go**, **Areas of concern** |
| `03-plan.md` | Engineer or tech lead | **Approval** section |
| The diff | Code owner | PR approval, branch protection |
| `04-review.md` | Code owner — never the agent | **Human decision** section |
| `05-deploy.md` | Release manager | **Gate** section |
| `06-lessons.md` | Service owner | Follow-up intents |

## Source of truth

Name one system as authoritative per artifact and have everything else reference
it. The failure mode is not choosing: two half-maintained records, and an audit
trail that proves nothing.

- **Repo as source of truth** — artifacts live in `intents/`, and MCP writes push
  a link and a status back to Jira or ServiceNow.
- **Legacy system as source of truth** — the ticket is authoritative, and the
  markdown artifacts are working copies carrying the record id in their header.

Either works. Write down which one you chose, in `CLAUDE.md`, where a session
will read it.
