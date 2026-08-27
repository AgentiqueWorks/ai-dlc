"""The package must validate cleanly against its own rules."""

from __future__ import annotations

from ai_dlc.validate import run_all


def test_no_errors(repo_root):
    problems = [p for p in run_all(repo_root) if p.level == "error"]
    assert not problems, "\n".join(p.format() for p in problems)


def test_no_warnings(repo_root):
    problems = [p for p in run_all(repo_root) if p.level == "warn"]
    assert not problems, "\n".join(p.format() for p in problems)
