#!/usr/bin/env python3
"""``ai-dlc backlog`` -- read the intents/ tree as a work queue.

In a GitHub-centric AI-DLC team the repository *is* the backlog: every intent is
a folder, its stage is the highest-numbered artifact it has produced, and its
branch is ``intent/<id>``. This command reports that queue without needing a
ticket system.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

from . import gitio, render
from .repo import ARTIFACTS, STATUSES, Intent, find_root, load_intents

__all__ = ["BacklogRow", "build", "main"]

EXIT_OK = 0
EXIT_ENVIRONMENT = 3

_CLOSED = ("done", "abandoned")

# Fallback when an artifact does not declare "- **Status:**".
_STAGE_STATUS = {
    "01-plan": "draft",
    "02-design": "in-progress",
    "03-build": "in-progress",
    "04-test": "in-review",
    "05-deploy": "in-progress",
    "06-maintain": "done",
}


@dataclass(frozen=True)
class BacklogRow:
    id: str
    title: Optional[str]
    stage: str
    status: str
    chain: str
    branch: Optional[str]
    landed: bool
    last_activity: Optional[datetime]
    age_days: Optional[int]
    stale: bool
    next_artifact: Optional[str]


def _next_artifact(intent: Intent) -> Optional[str]:
    for name in ARTIFACTS:
        if name not in intent.artifacts:
            return name
    return None


def build(root: Path, stale_days: int = 30, use_git: bool = True) -> List[BacklogRow]:
    root = Path(root).expanduser().resolve()
    intents = load_intents(root, use_git=use_git)

    git_ok = use_git and gitio.git_available() and gitio.repo_root(root) is not None
    shallow = git_ok and gitio.is_shallow(root)
    last_touch = {}
    default = ""
    if git_ok and not shallow:
        last_touch = gitio.last_touch_times(root, "intents/")
        default = gitio.default_branch(root)

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=stale_days)
    rows: List[BacklogRow] = []

    for intent in intents:
        prefix = f"intents/{intent.id}/"
        stamps = [v for k, v in last_touch.items() if k.startswith(prefix)]
        activity = max(stamps) if stamps else None
        if activity and not activity.tzinfo:
            activity = activity.replace(tzinfo=timezone.utc)

        landed = False
        branch = None
        if git_ok and not shallow:
            landed = gitio.landed_time(root, default, prefix + "01-intent.md") is not None
            branch = gitio.branch_for_intent(root, intent.id)

        stage = intent.stage
        status = intent.status or _STAGE_STATUS.get(stage, "draft")
        stale = bool(activity and activity < cutoff and status not in _CLOSED)
        if stale and branch is None and not landed:
            status = "abandoned"

        rows.append(
            BacklogRow(
                id=intent.id,
                title=intent.title,
                stage=stage,
                status=status,
                chain=intent.chain,
                branch=branch,
                landed=landed,
                last_activity=activity,
                age_days=(now - activity).days if activity else None,
                stale=stale,
                next_artifact=_next_artifact(intent),
            )
        )
    return rows


def _filter(rows: List[BacklogRow], statuses, stages, show_all: bool) -> List[BacklogRow]:
    out = rows
    if not show_all:
        out = [r for r in out if r.status not in _CLOSED]
    if statuses:
        wanted = {s.strip().lower() for s in statuses}
        out = [r for r in out if r.status in wanted]
    if stages:
        wanted = {s.strip().lower() for s in stages}
        out = [r for r in out if r.stage in wanted or r.stage.split("-")[0] in wanted]
    return out


def _sort(rows: List[BacklogRow], key: str) -> List[BacklogRow]:
    if key == "age":
        return sorted(rows, key=lambda r: (r.age_days is None, -(r.age_days or 0)))
    if key == "stage":
        return sorted(rows, key=lambda r: (r.stage, r.id))
    return sorted(rows, key=lambda r: r.id)


def render_table(rows: List[BacklogRow], total: int, wide: bool, stale_days: int) -> str:
    headers = ["ID", "STAGE", "STATUS", "CHAIN", "NEXT", "AGE"]
    if wide:
        headers.insert(1, "TITLE")
        headers.append("BRANCH")
    body = []
    for row in rows:
        age = f"{row.age_days}d" if row.age_days is not None else "—"
        if row.stale:
            age += " stale"
        cells = [row.id, row.stage, row.status, row.chain, row.next_artifact or "—", age]
        if wide:
            cells.insert(1, (row.title or "—")[:44])
            cells.append(row.branch or "—")
        body.append(cells)

    hidden = total - len(rows)
    stale_count = sum(1 for r in rows if r.stale)
    summary = f"{len(rows)} open · {stale_count} stale (>{stale_days}d)"
    if hidden > 0:
        summary += f" · {hidden} hidden (--all to show)"
    return render.table(headers, body) + "\n\n" + summary


def render_markdown(rows: List[BacklogRow]) -> str:
    body = [
        [r.id, r.stage, r.status, r.chain, r.next_artifact or "—", f"{r.age_days}d" if r.age_days is not None else "—"]
        for r in rows
    ]
    return render.markdown_table(["Intent", "Stage", "Status", "Chain", "Next", "Age"], body)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-dlc backlog", description="Show the intents/ backlog")
    parser.add_argument("path", nargs="?", default=".", help="Path inside an AI-DLC project")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--markdown", action="store_true", help="Emit a Markdown table")
    parser.add_argument("--status", help="Comma-separated statuses to include (%s)" % ", ".join(STATUSES))
    parser.add_argument("--stage", help="Comma-separated stages to include, e.g. 03 or 03-build")
    parser.add_argument("--all", action="store_true", dest="show_all", help="Include done and abandoned intents")
    parser.add_argument("--sort", choices=["id", "age", "stage"], default="id")
    parser.add_argument("--stale-days", type=int, default=30)
    parser.add_argument("--wide", action="store_true", help="Include title and branch columns")
    parser.add_argument("--no-git", action="store_true", help="Skip git lookups (faster, no branch or age)")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    start = Path(args.path).expanduser().resolve()
    root = find_root(start)
    if root is None:
        message = "no AI-DLC layout found (expected an intents/ directory). Run `ai-dlc init-repo .` first."
        if args.json:
            print(json.dumps({"schema": 1, "root": str(start), "intents": []}, indent=2))
        else:
            print(message, file=sys.stderr)
        return EXIT_ENVIRONMENT

    rows = build(root, stale_days=args.stale_days, use_git=not args.no_git)
    if not rows and not (root / "intents").is_dir():
        message = "no AI-DLC layout found (expected an intents/ directory). Run `ai-dlc init-repo .` first."
        if args.json:
            print(json.dumps({"schema": 1, "root": str(root), "intents": []}, indent=2))
        else:
            print(message, file=sys.stderr)
        return EXIT_ENVIRONMENT
    total = len(rows)
    selected = _sort(
        _filter(
            rows,
            args.status.split(",") if args.status else None,
            args.stage.split(",") if args.stage else None,
            args.show_all,
        ),
        args.sort,
    )

    if args.json:
        print(
            json.dumps(
                {"schema": 1, "root": str(root), "intents": [asdict(r) for r in selected]},
                indent=2,
                default=str,
            )
        )
    elif args.markdown:
        print(render_markdown(selected))
    else:
        print(render_table(selected, total, args.wide, args.stale_days))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
