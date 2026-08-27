#!/usr/bin/env python3
"""The AI-DLC repository model: intents and their artifact chain.

An AI-DLC project keeps its backlog in ``intents/<intent-id>/`` where each
stage of the loop commits one numbered artifact:

    01-intent.md  02-spec.md  03-plan.md  04-review.md  05-deploy.md  06-lessons.md

This module reads that layout. It is deliberately git-free so that ``backlog``
and the filesystem indicators still work in a plain directory.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

__all__ = [
    "ARTIFACTS",
    "STAGE_BY_ARTIFACT",
    "STATUSES",
    "Intent",
    "find_root",
    "load_intents",
    "parse_field",
    "parse_planned_files",
    "stage_reached",
]

ARTIFACTS: tuple[str, ...] = (
    "01-intent.md",
    "02-spec.md",
    "03-plan.md",
    "04-review.md",
    "05-deploy.md",
    "06-lessons.md",
)

STAGE_BY_ARTIFACT: dict[str, str] = {
    "01-intent.md": "01-plan",
    "02-spec.md": "02-design",
    "03-plan.md": "03-build",
    "04-review.md": "04-test",
    "05-deploy.md": "05-deploy",
    "06-lessons.md": "06-maintain",
}

STATUSES: tuple[str, ...] = (
    "draft",
    "approved",
    "in-progress",
    "in-review",
    "blocked",
    "done",
    "abandoned",
)

# "- **Status:** approved" / "* **Signal at:** 2026-08-26T09:00:00Z"
_FIELD_RE_TMPL = r"^\s*[-*]\s*\*\*{label}:?\*\*\s*(?P<value>.+?)\s*$"
_HEADING_RE = re.compile(r"^#{2,6}\s+(?P<title>.+?)\s*$")
_BULLET_RE = re.compile(r"^\s*[-*]\s+(?P<item>.+?)\s*$")
_H1_RE = re.compile(r"^#\s+(?P<title>.+?)\s*$", re.MULTILINE)


def parse_field(markdown: str, label: str) -> str | None:
    """Read a ``- **Label:** value`` line out of an artifact."""
    pattern = re.compile(_FIELD_RE_TMPL.format(label=re.escape(label)), re.IGNORECASE | re.MULTILINE)
    match = pattern.search(markdown)
    if not match:
        return None
    value = match.group("value").strip()
    if value.startswith("<") and value.endswith(">"):
        return None  # unfilled template placeholder
    return value


def parse_title(markdown: str) -> str | None:
    match = _H1_RE.search(markdown)
    if not match:
        return None
    title = match.group("title").strip()
    # "Intent: Add CSV export" -> "Add CSV export"
    for prefix in ("Intent:", "Spec:", "Plan:", "Review:", "Deploy:", "Lessons:"):
        if title.startswith(prefix):
            title = title[len(prefix):].strip()
    if title.startswith("<") and title.endswith(">"):
        return None
    return title or None


def parse_planned_files(markdown: str, heading: str = "Files that change") -> list[str]:
    """Extract the bullet list under ``## Files that change`` from a plan.

    This is the parse contract that ``plan-diff-alignment`` depends on. Entries
    are stripped of backticks and trailing annotations such as ``(new)``.
    """
    lines = markdown.splitlines()
    collecting = False
    items: list[str] = []
    for line in lines:
        heading_match = _HEADING_RE.match(line)
        if heading_match:
            title = heading_match.group("title").strip().rstrip(":")
            if title.lower() == heading.lower():
                collecting = True
                continue
            if collecting:
                break
            continue
        if not collecting:
            continue
        bullet = _BULLET_RE.match(line)
        if bullet:
            item = bullet.group("item").strip()
            item = item.strip("`")
            item = re.sub(r"\s*[—-]\s.*$", "", item)
            item = re.sub(r"\s*\((new|modified|deleted|added)\)\s*$", "", item, flags=re.IGNORECASE)
            item = item.strip().strip("`").strip()
            if item and not (item.startswith("<") and item.endswith(">")):
                items.append(item)
    return items


@dataclass(frozen=True)
class Intent:
    """One folder under ``intents/``."""

    id: str
    path: Path
    artifacts: dict[str, Path] = field(default_factory=dict)
    title: str | None = None
    status: str | None = None
    signal_at: datetime | None = None
    planned_files: tuple[str, ...] = ()
    ref: str | None = None  # None when the intent is in the working tree

    @property
    def stage(self) -> str:
        return stage_reached(self)

    @property
    def chain(self) -> str:
        return "".join("●" if name in self.artifacts else "○" for name in ARTIFACTS)

    @property
    def completeness(self) -> float:
        return len(self.artifacts) / len(ARTIFACTS)


def stage_reached(intent: Intent) -> str:
    """The stage of the highest-numbered artifact present."""
    highest = "00-onboarding"
    for name in ARTIFACTS:
        if name in intent.artifacts:
            highest = STAGE_BY_ARTIFACT[name]
    return highest


def _parse_signal_at(markdown: str) -> datetime | None:
    raw = parse_field(markdown, "Signal at")
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def find_root(start: Path) -> "Path | None":
    """Find the AI-DLC project root.

    An explicit marker wins: a ``.ai-dlc/`` directory or a checked-out
    ``intents/``. Failing that, the git top level is the root -- under the
    one-branch-per-intent convention the backlog often exists only on unmerged
    branches, so an on-disk ``intents/`` is not a reliable signal.
    """
    from . import gitio

    current = Path(start).expanduser().resolve()
    for candidate in [current, *current.parents]:
        if (candidate / ".ai-dlc").is_dir() or (candidate / "intents").is_dir():
            return candidate
        if (candidate / ".git").exists():
            break

    if gitio.git_available():
        top = gitio.repo_root(current)
        if top is not None:
            return top
    return None


def _fs_reader(root: Path):
    def read(rel: str) -> str:
        return (Path(root) / rel).read_text(encoding="utf-8", errors="replace")

    return read


def _git_reader(root: Path, ref: str):
    from . import gitio

    def read(rel: str) -> str:
        return gitio.show(Path(root), ref, rel)

    return read


def _discover_sources(root: Path) -> Dict[str, Tuple[str, Dict[str, str]]]:
    """Map each intent id to the best source for its artifacts.

    The working tree wins when the folder is checked out. Otherwise the intent's
    own branch is used, so an in-flight intent that has not landed on the default
    branch is still part of the backlog -- which is the whole point of the
    one-branch-per-intent convention.
    """
    from . import gitio

    sources: Dict[str, Tuple[str, Dict[str, str]]] = {}

    intents_dir = Path(root) / "intents"
    if intents_dir.is_dir():
        for folder in sorted(p for p in intents_dir.iterdir() if p.is_dir()):
            found = {
                name: f"intents/{folder.name}/{name}"
                for name in ARTIFACTS
                if (folder / name).is_file()
            }
            if found:
                sources[folder.name] = ("", found)

    if not (gitio.git_available() and gitio.repo_root(Path(root))):
        return sources
    if gitio.is_shallow(Path(root)):
        return sources

    for ref in gitio.intent_refs(Path(root)):
        for rel in gitio.ls_tree(Path(root), ref, "intents/"):
            parts = rel.split("/")
            if len(parts) != 3 or parts[0] != "intents" or parts[2] not in ARTIFACTS:
                continue
            intent_id, artifact = parts[1], parts[2]
            existing = sources.get(intent_id)
            if existing and existing[0] == "":
                continue  # the working tree already has it
            if existing is None:
                sources[intent_id] = (ref, {artifact: rel})
            else:
                existing[1][artifact] = rel
    return sources


def load_intents(root: Path, use_git: bool = True) -> List["Intent"]:
    """Load every intent, from the working tree and from unmerged intent branches."""
    root = Path(root)
    sources = _discover_sources(root) if use_git else {}
    if not use_git:
        intents_dir = root / "intents"
        if intents_dir.is_dir():
            for folder in sorted(p for p in intents_dir.iterdir() if p.is_dir()):
                found = {
                    name: f"intents/{folder.name}/{name}"
                    for name in ARTIFACTS
                    if (folder / name).is_file()
                }
                if found:
                    sources[folder.name] = ("", found)

    intents: List[Intent] = []
    for intent_id in sorted(sources):
        ref, found = sources[intent_id]
        read = _fs_reader(root) if ref == "" else _git_reader(root, ref)
        artifacts = {name: root / rel for name, rel in found.items()}

        title = status = None
        signal_at = None
        planned: List[str] = []
        texts: Dict[str, str] = {}

        for name, rel in found.items():
            try:
                texts[name] = read(rel)
            except OSError:
                texts[name] = ""

        first = texts.get("01-intent.md")
        if first:
            title = parse_title(first)
            signal_at = _parse_signal_at(first)

        for name in reversed(ARTIFACTS):
            text = texts.get(name)
            if not text:
                continue
            value = parse_field(text, "Status")
            if value:
                status = value.strip().lower()
                break

        plan = texts.get("03-plan.md")
        if plan:
            planned = parse_planned_files(plan)

        intents.append(
            Intent(
                id=intent_id,
                path=root / "intents" / intent_id,
                artifacts=artifacts,
                title=title,
                status=status,
                signal_at=signal_at,
                planned_files=tuple(planned),
                ref=ref or None,
            )
        )
    return intents
