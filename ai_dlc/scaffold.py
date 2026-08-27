#!/usr/bin/env python3
"""Scaffold and migrate an AI-DLC project layout.

Layout v2 puts the backlog in ``intents/<id>/`` with numbered artifacts, which
is what every skill in this package reads and writes. Layout v1 used flat
``intent/``, ``spec/`` and ``plan/`` directories; ``ai-dlc migrate`` moves a v1
project forward without losing content.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from . import gitio

__all__ = [
    "LAYOUT_VERSION",
    "Action",
    "detect_layout",
    "scaffold",
    "plan_migration",
    "apply_migration",
    "build_init_parser",
    "build_migrate_parser",
    "main",
]

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
LAYOUT_VERSION = 2

# Flat v1 directories and the artifact each one held.
_V1_MAP = {"intent": "01-intent.md", "spec": "02-spec.md", "plan": "03-plan.md"}

CLIENT_SKILL_DIRS: Dict[str, str] = {
    "claude": ".claude/skills",
    "codex": ".codex/skills",
    "agents": ".agents/skills",
    "github": ".github/skills",
}

ARTIFACT_TEMPLATES = (
    "01-intent.md",
    "02-spec.md",
    "03-plan.md",
    "04-review.md",
    "05-deploy.md",
    "06-lessons.md",
    "metrics.md",
)

# Copied to the project root, where the skills expect to find them as singletons.
ROOT_TEMPLATES = {
    "CLAUDE.md": "CLAUDE.md",
    "AGENTS.md": "AGENTS.md",
    "REVIEW.md": "REVIEW.md",
    "bands.yaml": "bands.yaml",
}

INTENTS_README = """# Intents — the backlog

Every unit of work is a folder here, named `<slug>-<YYYYMMDD>`, holding the
artifact chain the AI-Native SDLC loop produces:

| File | Stage | Written by |
|---|---|---|
| `01-intent.md` | Plan | `01-intent-capture` |
| `02-spec.md` | Design | `02-spec-writer` |
| `03-plan.md` | Build | `03-plan-mode` |
| `04-review.md` | Deploy | `05-pr-review` |
| `05-deploy.md` | Deploy | `05-release-gate` |
| `06-lessons.md` | Maintain | `06-closing-the-loop` |

One branch per intent: `intent/<id>`. One PR per intent. A human merges when the
whole chain is accepted.

Run `ai-dlc backlog` to see the queue and `ai-dlc metrics` to measure it.
"""

LAYOUT_NOTE = """# This file records which AI-DLC layout the project uses so that
# `ai-dlc migrate` can act deterministically instead of guessing.
"""


@dataclass(frozen=True)
class Action:
    kind: str  # "create" | "copy" | "move" | "skip" | "chmod"
    dst: Path
    src: Optional[Path] = None
    reason: str = ""

    def describe(self, base: Path) -> str:
        try:
            shown = self.dst.relative_to(base)
        except ValueError:
            shown = self.dst
        suffix = f" ({self.reason})" if self.reason else ""
        return f"{self.kind:>6}  {shown}{suffix}"


# Artifact templates renamed in layout v2, so a vendored copy of templates/
# from an older release still carries the old names.
_V1_TEMPLATES = {"intent.md": "01-intent.md", "spec.md": "02-spec.md", "plan.md": "03-plan.md"}


def _v1_signals(target: Path) -> bool:
    if any((target / name).is_dir() for name in _V1_MAP):
        return True
    if any((target / name).is_file() for name in ("intent.md", "spec.md", "plan.md")):
        return True
    # A vendored templates/ directory using the pre-0.3.0 artifact names.
    return any((target / "templates" / old).is_file() for old in _V1_TEMPLATES)


def detect_layout(target: Path) -> int:
    """2 = current layout, 1 = an older layout that needs migrating, 0 = not an
    AI-DLC project.

    The v1 signals are checked before ``intents/`` on purpose: a project can have
    adopted ``intents/<id>/`` while still carrying a vendored ``templates/``
    directory with the pre-0.3.0 artifact names, and that still needs migrating.
    """
    target = Path(target)
    marker = target / ".ai-dlc" / "layout.json"
    if marker.is_file():
        try:
            return int(json.loads(_strip_comments(marker.read_text(encoding="utf-8"))).get("layout_version", LAYOUT_VERSION))
        except (json.JSONDecodeError, ValueError, TypeError):
            return LAYOUT_VERSION
    if _v1_signals(target):
        return 1
    if (target / "intents").is_dir():
        return 2
    return 0


def _strip_comments(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))


def _write(path: Path, content: str, actions: List[Action], dry_run: bool, force: bool, reason: str = "") -> None:
    if path.exists() and not force:
        actions.append(Action("skip", path, reason="already exists"))
        return
    actions.append(Action("create", path, reason=reason))
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _copy(src: Path, dst: Path, actions: List[Action], dry_run: bool, force: bool, mode: int = 0) -> None:
    if not src.exists():
        actions.append(Action("skip", dst, src, "source missing"))
        return
    if dst.exists() and not force:
        actions.append(Action("skip", dst, src, "already exists"))
        return
    actions.append(Action("copy", dst, src))
    if dry_run:
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        shutil.copy2(src, dst)
        if mode:
            dst.chmod(mode)


def scaffold(
    target: Path,
    client: str = "claude",
    force: bool = False,
    with_ci: bool = False,
    dry_run: bool = False,
) -> List[Action]:
    """Create layout v2 in ``target``. Never deletes anything the user owns."""
    target = Path(target).expanduser().resolve()
    actions: List[Action] = []
    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)

    for directory in ("intents", "evals", "templates", ".claude/hooks", ".claude/agents", ".github"):
        path = target / directory
        if not dry_run:
            path.mkdir(parents=True, exist_ok=True)

    _write(target / "intents" / "README.md", INTENTS_README, actions, dry_run, force)
    _write(target / "evals" / ".gitkeep", "", actions, dry_run, force)

    for name in ARTIFACT_TEMPLATES:
        _copy(PACKAGE_ROOT / "templates" / name, target / "templates" / name, actions, dry_run, force)

    for source, destination in ROOT_TEMPLATES.items():
        _copy(PACKAGE_ROOT / "templates" / source, target / destination, actions, dry_run, force)

    for hook in sorted((PACKAGE_ROOT / "governance" / "hooks").glob("*.sh")):
        if hook.name == "hook-template.sh":
            continue
        _copy(hook, target / ".claude" / "hooks" / hook.name, actions, dry_run, force, mode=0o755)

    _copy(PACKAGE_ROOT / "governance" / "settings.json", target / ".claude" / "settings.json", actions, dry_run, force)

    agents_src = PACKAGE_ROOT / "templates" / "agents"
    if agents_src.is_dir():
        for agent in sorted(agents_src.glob("*.md")):
            _copy(agent, target / ".claude" / "agents" / agent.name, actions, dry_run, force)

    _copy(
        PACKAGE_ROOT / ".github" / "copilot-instructions.md",
        target / ".github" / "copilot-instructions.md",
        actions,
        dry_run,
        force,
    )

    if with_ci:
        workflows = PACKAGE_ROOT / "templates" / "workflows"
        for workflow in sorted(workflows.glob("*.yml")):
            _copy(workflow, target / ".github" / "workflows" / workflow.name, actions, dry_run, force)

    clients = list(CLIENT_SKILL_DIRS) if client == "all" else [client]
    for name in clients:
        destination = target / CLIENT_SKILL_DIRS[name]
        for skill in sorted(d for d in (PACKAGE_ROOT / "skills").iterdir() if d.is_dir()):
            _copy(skill, destination / skill.name, actions, dry_run, force)

    _write(
        target / ".ai-dlc" / "layout.json",
        LAYOUT_NOTE
        + json.dumps({"layout_version": LAYOUT_VERSION, "client": client}, indent=2)
        + "\n",
        actions,
        dry_run,
        force=True,
    )
    return actions


# ------------------------------------------------------------------ migration

def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plan_migration(target: Path) -> List[Action]:
    """Plan the moves that take a layout v1 project to layout v2."""
    target = Path(target).expanduser().resolve()
    actions: List[Action] = []
    if detect_layout(target) != 1:
        return actions

    for directory, artifact in _V1_MAP.items():
        source_dir = target / directory
        if not source_dir.is_dir():
            continue
        for path in sorted(source_dir.glob("*.md")):
            slug = path.stem
            actions.append(Action("move", target / "intents" / slug / artifact, path, f"from {directory}/"))

    for name, artifact in (("intent.md", "01-intent.md"), ("spec.md", "02-spec.md"), ("plan.md", "03-plan.md")):
        path = target / name
        if not path.is_file():
            continue
        shipped = PACKAGE_ROOT / "templates" / artifact
        legacy = PACKAGE_ROOT / "templates" / name
        is_template = False
        for candidate in (shipped, legacy):
            if candidate.is_file() and _sha256(candidate) == _sha256(path):
                is_template = True
                break
        if is_template:
            actions.append(Action("move", target / "templates" / artifact, path, "unmodified template"))
        else:
            actions.append(Action("skip", path, path, "modified by you; move it into intents/<id>/ yourself"))

    # A vendored templates/ directory from before 0.3.0 keeps the old names.
    for old, new in _V1_TEMPLATES.items():
        source = target / "templates" / old
        if not source.is_file():
            continue
        destination = target / "templates" / new
        if destination.exists():
            actions.append(Action("skip", source, source, f"{new} already exists"))
            continue
        actions.append(Action("move", destination, source, "renamed artifact template"))

    # Templates the chain gained in 0.3.0. Reported, then copied, never silently
    # overwriting anything the project already has.
    if (target / "templates").is_dir():
        for name in ARTIFACT_TEMPLATES + tuple(ROOT_TEMPLATES):
            shipped = PACKAGE_ROOT / "templates" / name
            destination = target / "templates" / name
            if shipped.is_file() and not destination.exists() and name not in _V1_TEMPLATES.values():
                actions.append(Action("copy", destination, shipped, "new in this release"))

    actions.append(Action("create", target / ".ai-dlc" / "layout.json", reason=f"layout_version {LAYOUT_VERSION}"))
    return actions


def apply_migration(actions: List[Action], target: Path, use_git: bool = True) -> None:
    target = Path(target).expanduser().resolve()
    git_ok = use_git and gitio.git_available() and gitio.repo_root(target) is not None
    for action in actions:
        if action.kind == "move" and action.src:
            action.dst.parent.mkdir(parents=True, exist_ok=True)
            if git_ok:
                out = gitio.git(["mv", str(action.src), str(action.dst)], target, check=False)
                if out == "" and not action.dst.exists():
                    shutil.move(str(action.src), str(action.dst))
            else:
                shutil.move(str(action.src), str(action.dst))
        elif action.kind == "copy" and action.src:
            action.dst.parent.mkdir(parents=True, exist_ok=True)
            if not action.dst.exists():
                shutil.copy2(action.src, action.dst)
        elif action.kind == "create" and action.dst.name == "layout.json":
            action.dst.parent.mkdir(parents=True, exist_ok=True)
            action.dst.write_text(
                LAYOUT_NOTE + json.dumps({"layout_version": LAYOUT_VERSION}, indent=2) + "\n",
                encoding="utf-8",
            )

    for directory in _V1_MAP:
        path = target / directory
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()


# ------------------------------------------------------------------------ CLI


def build_init_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-dlc init-repo", description="Scaffold an AI-DLC project")
    parser.add_argument("target", help="Path to the target repository")
    parser.add_argument("--client", default="claude", choices=[*CLIENT_SKILL_DIRS, "all"])
    parser.add_argument("--with-ci", action="store_true", help="Also install the GitHub Actions workflow templates")
    parser.add_argument("--force", action="store_true", help="Overwrite files that already exist")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without writing")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_init_parser().parse_args(argv)
    target = Path(args.target).expanduser().resolve()

    existing = detect_layout(target)
    if existing == 1:
        print(f"{target} uses the old flat layout. Run `ai-dlc migrate {target}` first.", file=sys.stderr)
        return 3

    actions = scaffold(target, args.client, force=args.force, with_ci=args.with_ci, dry_run=args.dry_run)
    for action in actions:
        print(action.describe(target))

    created = sum(1 for a in actions if a.kind in ("create", "copy"))
    skipped = sum(1 for a in actions if a.kind == "skip")
    prefix = "Would scaffold" if args.dry_run else "Scaffolded"
    print(f"\n{prefix} AI-DLC layout v{LAYOUT_VERSION} at {target}: {created} written, {skipped} left alone")
    if not args.dry_run:
        print("Next: `ai-dlc backlog` to see the queue, `ai-dlc metrics` to measure it.")
        print("Configure MCP by copying mcp/claude-mcp.json (or copilot-mcp.json / codex-mcp.toml) into place.")
    return 0


def build_migrate_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-dlc migrate", description="Move a project to the current AI-DLC layout")
    parser.add_argument("path", nargs="?", default=".", help="Project to migrate")
    parser.add_argument("--apply", action="store_true", help="Perform the moves (default is a dry run)")
    parser.add_argument("--force", action="store_true", help="Migrate even with a dirty working tree")
    return parser


def migrate_main(argv: Optional[List[str]] = None) -> int:
    args = build_migrate_parser().parse_args(argv)

    target = Path(args.path).expanduser().resolve()
    layout = detect_layout(target)
    if layout >= LAYOUT_VERSION:
        print(f"{target} is already at layout v{LAYOUT_VERSION}; nothing to do.")
        return 0
    if layout == 0:
        print(f"{target} is not an AI-DLC project. Run `ai-dlc init-repo {target}`.", file=sys.stderr)
        return 3

    actions = plan_migration(target)
    for action in actions:
        print(action.describe(target))

    if not args.apply:
        print("\nDry run. Re-run with --apply to perform these moves.")
        return 0

    if gitio.git_available() and gitio.repo_root(target) and gitio.is_dirty(target) and not args.force:
        print("\nWorking tree is dirty. Commit or stash first, or pass --force.", file=sys.stderr)
        return 3

    apply_migration(actions, target)
    print(f"\nMigrated {target} to layout v{LAYOUT_VERSION}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
