# Contributing to AI-DLC

Thanks for helping make the AI-Native SDLC more usable.

## How to contribute

1. Open an issue describing the bug, gap, or idea.
2. Fork the repo and create a branch.
3. Make your changes.
4. Run `make` — validation and tests must pass.
5. Open a pull request with a clear description and the commands you tested.

## What we look for

- **Markdown-first**: the project stays instruction-driven. Prefer new `SKILL.md` files, templates, or references over code.
- **Cross-platform**: changes should work for Claude Code, Codex, and Copilot users where possible.
- **No secrets**: never commit tokens, `.env` files, or credentials.
- **Validation**: new skills must pass `make validate`; new MCP servers must be added to `mcp/configs/` and then `make mcp-sync`.

## Releasing

Maintainers bump `pyproject.toml` version, update `CHANGELOG.md`, and push a tag. CI creates a release automatically.