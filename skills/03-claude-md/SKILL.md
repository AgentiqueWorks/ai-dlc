---
name: 03-claude-md
description: Generate or update a project CLAUDE.md from the repository's build commands, conventions, architecture, and common mistakes. Use when onboarding an agent to a repo.
---

# CLAUDE.md maintainer

## Job

Create or refresh a project `CLAUDE.md` so every agent session starts with the right context.

## Who uses this

- **Platform engineers** setting up a new repo for agentic development.
- **Senior engineers** who want to capture the mistakes the agent keeps making.
- **Any contributor** who finds a recurring mistake and wants to stop it from recurring.

## Example prompts

- "Inspect this repo and write a `CLAUDE.md` that a new joiner would need."
- "Update `CLAUDE.md` now that we switched from npm to pnpm."
- "Claude keeps bumping dependency versions. Add a rule to `CLAUDE.md`."

## Steps

1. Inspect the repo: `README.md`, `package.json`, `Cargo.toml`, `pyproject.toml`, `Makefile`, build scripts, test and lint commands, and the top-level directory layout.
2. Interview the most senior engineer for:
   - how to build, test, and lint
   - naming and architecture conventions
   - the mistakes the agent repeats
   - frozen or protected paths
3. Write a concise `CLAUDE.md` using `templates/CLAUDE.md`.
4. Keep it under one page; move long reference material to `references/`.
5. Suggest a rule: when the agent makes a mistake twice, the correction goes into `CLAUDE.md`.

## Output

- A repo-level `CLAUDE.md` committed at the project root.
- A one-page context file that every agent session loads.