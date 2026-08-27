"""CLI wiring: every subcommand resolves, and the docs agree with the parser."""

from __future__ import annotations

import pytest

from ai_dlc import cli


EXPECTED = {"validate", "mcp-sync", "install", "init-repo", "migrate", "backlog", "metrics", "adoption"}


def subcommands():
    parser = cli.build_parser()
    names = set()
    for action in parser._subparsers._group_actions:
        names.update(getattr(action, "choices", {}) or {})
    return names


def test_every_subcommand_is_registered():
    assert subcommands() == EXPECTED


@pytest.mark.parametrize("command", sorted(EXPECTED))
def test_each_subcommand_dispatches(command, capsys):
    """Dispatch must resolve for every command: no ImportError, no typo in a
    module path. --help exits 0 from the subcommand's own parser."""
    with pytest.raises(SystemExit) as exc:
        cli.main([command, "--help"])
    assert exc.value.code == 0
    assert f"ai-dlc {command}" in capsys.readouterr().out


def test_unknown_subcommand_errors():
    with pytest.raises(SystemExit):
        cli.main(["not-a-command"])


def test_version_flag():
    with pytest.raises(SystemExit) as exc:
        cli.main(["--version"])
    assert exc.value.code == 0


def test_docs_and_parser_agree(repo_root):
    from ai_dlc.validate import check_docs

    problems = [p for p in check_docs(repo_root) if p.level == "error"]
    assert not problems, "\n".join(p.format() for p in problems)
