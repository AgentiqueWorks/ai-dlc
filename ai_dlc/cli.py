#!/usr/bin/env python3
"""Small CLI for the ai-dlc package."""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run_validate() -> int:
    return subprocess.call([sys.executable, str(ROOT / "scripts" / "validate.py")])


def run_install(client: str) -> int:
    env = {"INSTALL_CLIENT": client}
    return subprocess.call(["bash", str(ROOT / "scripts" / "install.sh")], env={**dict(), **env})


def run_init_repo(target: Path, client: str) -> int:
    return subprocess.call([sys.executable, str(ROOT / "scripts" / "init-repo.py"), str(target), "--client", client])


def run_mcp_sync() -> int:
    return subprocess.call([sys.executable, str(ROOT / "scripts" / "mcp-sync.py")])


def main() -> int:
    parser = argparse.ArgumentParser(prog="ai-dlc", description="AI-Native SDLC tooling")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate", help="Validate skills and MCP configs")
    sub.add_parser("mcp-sync", help="Regenerate combined MCP JSON files")

    p_install = sub.add_parser("install", help="Install skills for a client")
    p_install.add_argument("client", default="claude", choices=["claude", "codex", "agents", "github"], nargs="?")

    p_init = sub.add_parser("init-repo", help="Scaffold an AI-DLC project")
    p_init.add_argument("target", help="Target repository path")
    p_init.add_argument("--client", default="claude", choices=["claude", "codex", "agents"])

    args = parser.parse_args()

    if args.command == "validate":
        return run_validate()
    if args.command == "mcp-sync":
        return run_mcp_sync()
    if args.command == "install":
        return run_install(args.client)
    if args.command == "init-repo":
        return run_init_repo(Path(args.target), args.client)

    return 1


if __name__ == "__main__":
    sys.exit(main())