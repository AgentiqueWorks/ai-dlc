# Organization policy skills

`02-spec-writer` and `05-pr-review` both load "the org skills that apply". These
are those skills: the place an organization's rules become operational instead of
tribal.

Copy a directory into `.claude/skills/` (or `.agents/skills/`), fill in the
placeholders with your actual policy, and put it through PR review with the
policy owner as the required reviewer. When the policy changes, the skill changes,
and the next session picks it up — that is the whole point.

| Template | Policy owner | Applied during |
|---|---|---|
| `security/` | Security lead | Design, Build, Review |
| `api-design/` | Platform or API lead | Design, Build, Review |
| `brand/` | Design lead | Design, Build |
| `ux-patterns/` | Design lead | Design, Build |

Keep each one specific and testable. "Follow security best practices" changes no
behaviour. "Never log a field named ssn, email, phone, or name" does.
