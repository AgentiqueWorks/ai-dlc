---
name: 03-claude-md
description: Generate or update a project CLAUDE.md from the repository's build commands, conventions, architecture, and common mistakes. Use when onboarding an agent to a repo.
---

# CLAUDE.md maintainer

## Job

Create or refresh a project `CLAUDE.md` so every agent session starts with the right context.

## Steps

1. Inspect the repo: `README.md`, `package.json`, `Makefile`, build scripts, test commands, lint rules, and directory layout.
2. Interview the engineer for the conventions that matter and the mistakes the agent repeats.
3. Write a concise `CLAUDE.md` using `templates/CLAUDE.md`.
4. Keep it under one page; move long reference material to separate files.
5. Suggest a git hook or PR check that triggers this refresh when build/test commands change.

## Output

- A repo-level `CLAUDE.md` committed at the project root.