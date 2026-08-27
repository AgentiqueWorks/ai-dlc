#!/usr/bin/env python3
"""``ai-dlc`` — the command line for the AI-Native SDLC package.

Every subcommand dispatches to an importable module rather than shelling out to
a script, so the behaviour is unit-testable and inherits the caller's
environment. ``scripts/*.py`` are thin wrappers over the same modules for people
who run the repo without installing it.
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from . import __version__

__all__ = ["build_parser", "main"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-dlc", description="AI-Native SDLC tooling")
    parser.add_argument("--version", action="version", version=f"ai-dlc {__version__}")
    sub = parser.add_subparsers(dest="command", required=True, metavar="<command>")

    sub.add_parser("validate", help="Validate skills, MCP configs, hooks, templates, and docs", add_help=False)
    sub.add_parser("mcp-sync", help="Regenerate the combined per-client MCP configs", add_help=False)
    sub.add_parser("install", help="Install skills into an agent client's skill directory", add_help=False)
    sub.add_parser("init-repo", help="Scaffold an AI-DLC project", add_help=False)
    sub.add_parser("migrate", help="Move an existing project to the current AI-DLC layout", add_help=False)
    sub.add_parser("backlog", help="Show the intents/ backlog as a work queue", add_help=False)
    sub.add_parser("metrics", help="Compute the locally derivable delivery indicators", add_help=False)
    sub.add_parser("adoption", help="Show the play dependency graph and rollout order", add_help=False)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()

    if not argv or argv[0] in ("-h", "--help", "--version"):
        parser.parse_args(argv or ["--help"])
        return 0

    command, rest = argv[0], argv[1:]

    if command == "validate":
        from .validate import main as run
    elif command == "mcp-sync":
        from .mcpsync import main as run
    elif command == "install":
        from .install import main as run
    elif command == "init-repo":
        from .scaffold import main as run
    elif command == "migrate":
        from .scaffold import migrate_main as run
    elif command == "backlog":
        from .backlog import main as run
    elif command == "metrics":
        from .metrics import main as run
    elif command == "adoption":
        from .adoption import main as run
    else:
        parser.parse_args(argv)  # produces the standard "invalid choice" error
        return 2

    return run(rest)


if __name__ == "__main__":
    sys.exit(main())
