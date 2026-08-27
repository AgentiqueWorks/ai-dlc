# Repository instructions

This repo is a set of cross-platform AI skills that operationalize an AI-native SDLC. When working in this repo:

- Skills are markdown bundles in `skills/<stage>-<name>/SKILL.md`.
- Each `SKILL.md` must have a `name` and `description` in YAML frontmatter.
- Use the templates in `templates/` as the source of truth for generated artifacts.
- MCP configuration is under `mcp/` and is intentionally credential-free.
- Run `make validate` after changing skills and `make test` before committing.

For outside repositories that install these skills, the skills guide the agent through Plan, Design, Build, Test, Deploy, and Maintain.