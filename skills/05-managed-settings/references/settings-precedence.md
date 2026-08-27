# Settings precedence and what belongs where

## Precedence, highest first

1. **Managed settings** — the OS policy path, deployed by MDM.
2. **Command-line flags** — for the current invocation only.
3. **Project local** — `.claude/settings.local.json`, not committed.
4. **Project shared** — `.claude/settings.json`, committed and reviewed.
5. **User** — `~/.claude/settings.json`.

Within permissions, `deny` beats `ask` beats `allow`, at every layer. A managed
`deny` therefore cannot be undone by any project or user setting, which is the
property the whole design rests on.

## Managed settings paths

| Platform | Path |
|---|---|
| macOS | `/Library/Application Support/ClaudeCode/managed-settings.json` |
| Linux / WSL | `/etc/claude-code/managed-settings.json` |
| Windows | `C:\ProgramData\ClaudeCode\managed-settings.json` |

Deploy through the same MDM channel as the rest of your endpoint policy. A file
an engineer can edit is not a managed setting.

## The sorting question

For each rule, ask: *would you accept an engineer turning this off during an
incident at 2am?*

- **No** → managed. Credential reads, self-approval, force-push to a default
  branch, sandbox, telemetry.
- **Yes, with a PR** → project settings. Frozen paths, ticket requirements,
  which hooks run.
- **Yes, freely** → user settings. Editor preferences, model choice, output
  style.

Most disagreements about "should this be managed" are really disagreements about
that question. Ask it explicitly and the answer usually settles.

## Sandbox notes

- The allowlist is domains, not URLs. `github.com` grants the whole host.
- Start from what the build and test suite actually reach, measured, not guessed.
- `allowUnixSockets` matters for local databases and Docker. Turning it off is
  strict and frequently correct; test before you ship it.
- Commands that manage their own isolation (`docker`, `podman`) usually need to
  be excluded from the sandbox rather than run inside it.
- A sandbox that blocks the test suite will be disabled by everyone within a day.
  Ship it against a real suite first.

## Exception register

Keep it in the repository, not in a ticket queue.

| Exception | Requested by | Approved by | Expires | Reason |
|---|---|---|---|---|
| `deploy.internal` added to allowlist | <name> | <security lead> | <date> | staging deploys |

Re-review on the expiry date. An exception with no expiry is a policy change that
skipped review.
