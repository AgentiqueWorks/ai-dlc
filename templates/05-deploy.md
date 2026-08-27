# Deploy: <title>

- **From review:** `intents/<id>/04-review.md`
- **Status:** in-progress
- **Environment:** <staging / production>
- **Release:** <tag, commit, or deployment id>

## Gate

- **Gate that ran:** <hook name, e.g. production-gate.sh>
- **Approval token:** <RELEASE_APPROVAL reference — the record, never the value>
- **Authorized by:** <release manager>
- **Authorized at:** <YYYY-MM-DDTHH:MM:SSZ>

## Rollout

1. <step>
2. <step>

## Verification after deploy

- [ ] <metric or check that must hold>
- [ ] <smoke test>

## Rollback

- **Runbook:** <path or url>
- **Trigger:** <the condition that means roll back>
- **Owner:** <who executes it>

## Outcome

- **Result:** <shipped | rolled back | partial>
- **Notes:** <what actually happened>
