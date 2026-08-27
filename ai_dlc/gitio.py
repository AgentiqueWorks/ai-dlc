#!/usr/bin/env python3
"""Thin, testable boundary over the ``git`` command line.

Every subprocess call in the package goes through here so the rest of the code
can be unit tested against a temporary repository and so failures degrade into
``None``/empty results instead of tracebacks.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

__all__ = [
    "GitError",
    "Commit",
    "git_available",
    "git",
    "repo_root",
    "is_shallow",
    "default_branch",
    "first_add_times",
    "last_touch_times",
    "landed_time",
    "branch_for_intent",
    "merge_base",
    "changed_files",
    "commits_since",
    "unmerged_branches",
    "is_dirty",
    "intent_refs",
    "ls_tree",
    "show",
]


class GitError(RuntimeError):
    """Raised when a git invocation fails and the caller asked for ``check``."""


@dataclass(frozen=True)
class Commit:
    sha: str
    authored_at: datetime
    files: tuple[str, ...]


def git_available() -> bool:
    return shutil.which("git") is not None


def git(args: list[str], cwd: Path, check: bool = True) -> str:
    """Run ``git *args`` in ``cwd`` and return stdout.

    With ``check=False`` a failing command returns an empty string instead of
    raising, which is what most read-only probes want.
    """
    if not git_available():
        if check:
            raise GitError("git is not installed")
        return ""
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        if check:
            raise GitError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
        return ""
    return proc.stdout


def repo_root(cwd: Path) -> Path | None:
    out = git(["rev-parse", "--show-toplevel"], cwd, check=False).strip()
    return Path(out) if out else None


def is_shallow(cwd: Path) -> bool:
    return git(["rev-parse", "--is-shallow-repository"], cwd, check=False).strip() == "true"


def is_dirty(cwd: Path) -> bool:
    return bool(git(["status", "--porcelain"], cwd, check=False).strip())


def default_branch(cwd: Path) -> str:
    ref = git(["symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"], cwd, check=False).strip()
    if ref:
        return ref
    configured = git(["config", "--get", "init.defaultBranch"], cwd, check=False).strip()
    candidates = [c for c in (configured, "main", "master") if c]
    for name in candidates:
        if git(["rev-parse", "--verify", "--quiet", name], cwd, check=False).strip():
            return name
    return git(["rev-parse", "--abbrev-ref", "HEAD"], cwd, check=False).strip() or "HEAD"


def _parse_iso(value: str) -> datetime | None:
    """Parse an ISO-8601 timestamp, including forms older Pythons reject.

    ``datetime.fromisoformat`` only accepts a trailing ``Z`` from 3.11 onward,
    and a ``+0000`` offset without a colon from 3.11 onward too. Git emits both
    depending on how the date was set, so normalize before parsing.
    """
    text = value.strip()
    if not text:
        return None
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    elif len(text) > 5 and text[-5] in "+-" and text[-3] != ":":
        text = text[:-2] + ":" + text[-2:]
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _walk_log(cwd: Path, extra: list[str], pathspec: str) -> list[tuple[datetime, list[str]]]:
    """Parse ``git log --name-only`` output into (timestamp, files) records.

    Author dates (``%aI``) are used rather than committer dates: a rebase
    rewrites the committer date, and what we are measuring is when a human
    actually produced the artifact.
    """
    out = git(
        ["log", "--all", "--date-order", "--format=C%x09%aI", "--name-only", *extra, "--", pathspec],
        cwd,
        check=False,
    )
    records: list[tuple[datetime, list[str]]] = []
    current: datetime | None = None
    files: list[str] = []
    for line in out.splitlines():
        if line.startswith("C\t"):
            if current is not None and files:
                records.append((current, files))
            current = _parse_iso(line[2:])
            files = []
        elif line.strip():
            files.append(line.strip())
    if current is not None and files:
        records.append((current, files))
    return records


def first_add_times(cwd: Path, pathspec: str = "intents/") -> dict[str, datetime]:
    """Map every path under ``pathspec`` to the time it was first added."""
    result: dict[str, datetime] = {}
    for when, files in _walk_log(cwd, ["--diff-filter=A"], pathspec):
        for path in files:
            existing = result.get(path)
            if existing is None or when < existing:
                result[path] = when
    return result


def last_touch_times(cwd: Path, pathspec: str = "intents/") -> dict[str, datetime]:
    """Map every path under ``pathspec`` to the time it was last modified."""
    result: dict[str, datetime] = {}
    for when, files in _walk_log(cwd, [], pathspec):
        for path in files:
            existing = result.get(path)
            if existing is None or when > existing:
                result[path] = when
    return result


def landed_time(cwd: Path, default: str, path: str) -> datetime | None:
    """When ``path`` first appeared on the default branch.

    ``--first-parent`` makes this correct under both merge commits and
    squash-merges.
    """
    out = git(
        ["log", "--first-parent", default, "--diff-filter=A", "--reverse", "--format=%aI", "--", path],
        cwd,
        check=False,
    )
    for line in out.splitlines():
        stamp = _parse_iso(line)
        if stamp:
            return stamp
    return None


def branch_for_intent(cwd: Path, intent_id: str) -> str | None:
    """Find a local or remote branch named ``intent/<id>``."""
    out = git(
        ["for-each-ref", "--format=%(refname:short)", "refs/heads", "refs/remotes"],
        cwd,
        check=False,
    )
    wanted = f"intent/{intent_id}"
    remote_match = None
    for name in (line.strip() for line in out.splitlines()):
        if name == wanted:
            return name
        if name.endswith("/" + wanted):
            remote_match = remote_match or name
    return remote_match


def merge_base(cwd: Path, base: str, tip: str) -> str | None:
    out = git(["merge-base", base, tip], cwd, check=False).strip()
    return out or None


def changed_files(cwd: Path, base: str, tip: str) -> list[str]:
    out = git(["diff", "--name-only", f"{base}...{tip}"], cwd, check=False)
    return [line.strip() for line in out.splitlines() if line.strip()]


def commits_since(cwd: Path, base: str, tip: str) -> list[Commit]:
    out = git(
        ["log", "--format=C%x09%H%x09%aI", "--name-only", f"{base}..{tip}"],
        cwd,
        check=False,
    )
    commits: list[Commit] = []
    sha: str | None = None
    when: datetime | None = None
    files: list[str] = []
    for line in out.splitlines():
        if line.startswith("C\t"):
            if sha and when:
                commits.append(Commit(sha, when, tuple(files)))
            _, _, rest = line.partition("\t")
            sha, _, stamp = rest.partition("\t")
            when = _parse_iso(stamp)
            files = []
        elif line.strip():
            files.append(line.strip())
    if sha and when:
        commits.append(Commit(sha, when, tuple(files)))
    return commits


def unmerged_branches(cwd: Path, default: str) -> set[str]:
    out = git(
        ["branch", "--all", "--no-merged", default, "--format=%(refname:short)"],
        cwd,
        check=False,
    )
    return {line.strip() for line in out.splitlines() if line.strip()}


def intent_refs(cwd: Path) -> list:
    """Local and remote branches that look like ``intent/<id>``.

    One branch per intent is the convention this package assumes, so these are
    the refs where in-flight work lives before it lands.
    """
    out = git(["for-each-ref", "--format=%(refname:short)", "refs/heads", "refs/remotes"], cwd, check=False)
    names = [line.strip() for line in out.splitlines() if line.strip()]
    seen: dict = {}
    for name in names:
        base = name.split("/", 1)[1] if name.startswith("origin/") else name
        if base.startswith("intent/"):
            seen.setdefault(base, name)  # a local branch wins over its remote
            if not name.startswith("origin/"):
                seen[base] = name
    return list(seen.values())


def ls_tree(cwd: Path, ref: str, pathspec: str = "intents/") -> list:
    """Every file path under ``pathspec`` as of ``ref``."""
    out = git(["ls-tree", "-r", "--name-only", ref, "--", pathspec], cwd, check=False)
    return [line.strip() for line in out.splitlines() if line.strip()]


def show(cwd: Path, ref: str, path: str) -> str:
    """File contents at ``ref``, or an empty string if it is not there."""
    return git(["show", f"{ref}:{path}"], cwd, check=False)
