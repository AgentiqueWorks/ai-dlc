"""Shared fixtures.

The git fixtures build a real repository in ``tmp_path`` with pinned author
dates, so latency assertions are exact rather than flaky, and never touch the
developer's global git config.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return ROOT


@pytest.fixture
def git_repo(tmp_path: Path):
    """A hermetic git repository with a helper for dated commits."""
    if not shutil.which("git"):
        pytest.skip("git is not installed")

    work = tmp_path / "project"
    work.mkdir()
    base = [
        "git",
        "-c",
        "user.email=test@example.com",
        "-c",
        "user.name=AI-DLC Test",
        "-c",
        "commit.gpgsign=false",
        "-c",
        "init.defaultBranch=main",
    ]

    def run(*args: str, when: str = "2026-01-01T00:00:00+00:00") -> str:
        env = dict(os.environ)
        env["GIT_AUTHOR_DATE"] = when
        env["GIT_COMMITTER_DATE"] = when
        env["GIT_CONFIG_GLOBAL"] = str(tmp_path / "gitconfig")
        env["GIT_CONFIG_SYSTEM"] = str(tmp_path / "gitconfig")
        proc = subprocess.run(
            base + list(args), cwd=str(work), capture_output=True, text=True, env=env
        )
        if proc.returncode != 0:
            raise AssertionError(f"git {' '.join(args)} failed: {proc.stderr}")
        return proc.stdout

    def write(rel: str, content: str) -> Path:
        path = work / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def commit(message: str, when: str) -> None:
        run("add", "-A", when=when)
        run("commit", "-m", message, when=when)

    run("init", "-q")
    work_helpers = type(
        "GitRepo",
        (),
        {"path": work, "run": staticmethod(run), "write": staticmethod(write), "commit": staticmethod(commit)},
    )
    return work_helpers
