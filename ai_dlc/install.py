#!/usr/bin/env python3
"""Install the canonical ``skills/`` tree into an agent client's skill directory."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional

__all__ = ["TARGETS", "install", "main"]

PACKAGE_ROOT = Path(__file__).resolve().parent.parent

# Where each client looks for skills. Home-directory targets are user-wide;
# the repo-relative ones are per-project.
TARGETS: Dict[str, str] = {
    "claude": "~/.claude/skills",
    "codex": "~/.codex/skills",
    "agents": "./.agents/skills",
    "github": "./.github/skills",
}


def resolve_target(client: str, base: Path = PACKAGE_ROOT) -> Path:
    raw = TARGETS[client]
    if raw.startswith("~"):
        return Path(raw).expanduser()
    return (Path(base) / raw[2:]).resolve()


def install(client: str, base: Path = PACKAGE_ROOT, dry_run: bool = False) -> List[Path]:
    """Copy every skill directory, replacing only the ones this package owns.

    Skill directories the user added themselves are left untouched: only the
    names present in ``skills/`` are removed and re-copied.
    """
    source = Path(base) / "skills"
    if not source.is_dir():
        raise SystemExit(f"no skills directory at {source}")
    target = resolve_target(client, base)
    installed: List[Path] = []
    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)
    for skill in sorted(d for d in source.iterdir() if d.is_dir() and not d.name.startswith(".")):
        destination = target / skill.name
        installed.append(destination)
        if dry_run:
            continue
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(skill, destination)
    return installed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-dlc install", description="Install skills for an agent client")
    parser.add_argument("client", nargs="?", default="claude", choices=sorted(TARGETS) + ["all"])
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    clients = sorted(TARGETS) if args.client == "all" else [args.client]
    for client in clients:
        installed = install(client, dry_run=args.dry_run)
        target = resolve_target(client)
        verb = "Would install" if args.dry_run else "Installed"
        print(f"{verb} {len(installed)} skills for {client} -> {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
