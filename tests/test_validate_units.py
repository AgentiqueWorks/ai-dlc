"""One test per Problem code, against synthetic skills in tmp_path."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from ai_dlc import validate


def make_package(tmp_path: Path, repo_root: Path) -> Path:
    """A minimal but valid package we can then break in one specific way."""
    root = tmp_path / "pkg"
    (root / "skills").mkdir(parents=True)
    for name in ("mcp/configs", "templates", "governance/hooks", "evals", "references"):
        (root / name).mkdir(parents=True, exist_ok=True)
    shutil.copy2(repo_root / "references" / "indicators.yaml", root / "references" / "indicators.yaml")
    for template in validate.REQUIRED_TEMPLATES:
        (root / "templates" / template).write_text("# template\n", encoding="utf-8")
    return root


def add_skill(root: Path, name: str, front: str = "", body: str = "") -> Path:
    directory = root / "skills" / name
    directory.mkdir(parents=True, exist_ok=True)
    default_front = f"""name: {name}
description: A description long enough to look real. Use it when testing.
allowed-tools:
  - Read
metadata:
  stage: "03-build"
  persona: "engineer"
  requires: ""
  produces: ""
  indicators: ""
  mcp: ""
  maturity: "beta"
"""
    default_body = "# T\n\n## Job\n\nx\n\n## Steps\n\n1. x\n\n## Output\n\n- x\n"
    path = directory / "SKILL.md"
    path.write_text("---\n" + (front or default_front) + "---\n\n" + (body or default_body), encoding="utf-8")
    return path


def codes(problems, level=None):
    return {p.code for p in problems if level is None or p.level == level}


def test_valid_skill_produces_no_skill_errors(tmp_path, repo_root):
    root = make_package(tmp_path, repo_root)
    add_skill(root, "03-thing")
    assert not codes(validate.check_skills(root), "error")


def test_unknown_top_level_key_is_an_error(tmp_path, repo_root):
    """The closed key set is what keeps frontmatter portable across clients."""
    root = make_package(tmp_path, repo_root)
    add_skill(
        root,
        "03-thing",
        front='name: 03-thing\ndescription: Long enough description here. Use when testing.\nstage: "03-build"\n',
    )
    assert "skill.frontmatter.unknown-key" in codes(validate.check_skills(root), "error")


def test_name_must_match_directory(tmp_path, repo_root):
    root = make_package(tmp_path, repo_root)
    add_skill(root, "03-thing", front="name: other\ndescription: Long enough description. Use when testing.\n")
    assert "skill.name.mismatch" in codes(validate.check_skills(root), "error")


def test_missing_required_heading(tmp_path, repo_root):
    root = make_package(tmp_path, repo_root)
    add_skill(root, "03-thing", body="# T\n\n## Job\n\nx\n")
    assert "skill.body.heading" in codes(validate.check_skills(root), "error")


def test_dangling_requires(tmp_path, repo_root):
    root = make_package(tmp_path, repo_root)
    add_skill(root, "03-thing", front=_front("03-thing", requires="03-missing"))
    assert "skill.metadata.requires" in codes(validate.check_skills(root), "error")


def test_dependency_cycle_is_detected(tmp_path, repo_root):
    root = make_package(tmp_path, repo_root)
    add_skill(root, "03-a", front=_front("03-a", requires="03-b"))
    add_skill(root, "03-b", front=_front("03-b", requires="03-a"))
    assert "skill.metadata.cycle" in codes(validate.check_skills(root), "error")


def test_unknown_indicator(tmp_path, repo_root):
    root = make_package(tmp_path, repo_root)
    add_skill(root, "03-thing", front=_front("03-thing", indicators="not-a-real-indicator"))
    assert "skill.metadata.indicator" in codes(validate.check_skills(root), "error")


def test_metadata_must_be_strings(tmp_path, repo_root):
    """The Skills API metadata contract is string-valued, so lists are refused."""
    root = make_package(tmp_path, repo_root)
    front = (
        "name: 03-thing\ndescription: Long enough description here. Use when testing.\n"
        "metadata:\n  stage: \"03-build\"\n  persona:\n    - engineer\n"
        "  requires: \"\"\n  produces: \"\"\n  indicators: \"\"\n  mcp: \"\"\n  maturity: \"beta\"\n"
    )
    add_skill(root, "03-thing", front=front)
    assert "skill.metadata.shape" in codes(validate.check_skills(root), "error")


def test_bad_allowed_tools_entry(tmp_path, repo_root):
    root = make_package(tmp_path, repo_root)
    front = (
        "name: 03-thing\ndescription: Long enough description here. Use when testing.\n"
        "allowed-tools:\n  - not a tool!\n"
        "metadata:\n  stage: \"03-build\"\n  persona: \"engineer\"\n  requires: \"\"\n"
        "  produces: \"\"\n  indicators: \"\"\n  mcp: \"\"\n  maturity: \"beta\"\n"
    )
    add_skill(root, "03-thing", front=front)
    assert "skill.allowed-tools.entry" in codes(validate.check_skills(root), "error")


def _front(name, requires="", indicators="", mcp="", persona="engineer"):
    return (
        f"name: {name}\ndescription: A description long enough to look real. Use when testing.\n"
        "allowed-tools:\n  - Read\n"
        f'metadata:\n  stage: "03-build"\n  persona: "{persona}"\n  requires: "{requires}"\n'
        f'  produces: ""\n  indicators: "{indicators}"\n  mcp: "{mcp}"\n  maturity: "beta"\n'
    )


def test_orphan_reference_is_a_warning(tmp_path, repo_root):
    root = make_package(tmp_path, repo_root)
    add_skill(root, "03-thing")
    refs = root / "skills" / "03-thing" / "references"
    refs.mkdir()
    (refs / "unused.md").write_text("nobody cites me\n", encoding="utf-8")
    assert "skill.body.orphan-reference" in codes(validate.check_skills(root), "warn")


def test_literal_secret_is_rejected(tmp_path, repo_root):
    root = make_package(tmp_path, repo_root)
    (root / "mcp" / "configs" / "leaky.json").write_text(
        json.dumps({"mcpServers": {"leaky": {"type": "http", "url": "https://x", "headers": {"Authorization": "Bearer ghp_" + "a" * 30}}}}),
        encoding="utf-8",
    )
    assert "secret.literal" in codes(validate.check_secrets(root), "error")


def test_mcp_placeholder_required(tmp_path, repo_root):
    root = make_package(tmp_path, repo_root)
    (root / "mcp" / "configs" / "svc.json").write_text(
        json.dumps({"mcpServers": {"svc": {"type": "stdio", "command": "npx", "env": {"API_TOKEN": "hunter2"}}}}),
        encoding="utf-8",
    )
    assert "mcp.placeholder" in codes(validate.check_mcp(root), "error")


def test_mcp_type_must_be_valid(tmp_path, repo_root):
    root = make_package(tmp_path, repo_root)
    (root / "mcp" / "configs" / "svc.json").write_text(
        json.dumps({"mcpServers": {"svc": {"type": "remote", "url": "https://x"}}}), encoding="utf-8"
    )
    assert "mcp.fragment.type" in codes(validate.check_mcp(root), "error")


def test_mcp_sync_drift_is_detected(tmp_path, repo_root):
    root = make_package(tmp_path, repo_root)
    (root / "mcp" / "configs" / "svc.json").write_text(
        json.dumps({"mcpServers": {"svc": {"type": "stdio", "command": "npx"}}}), encoding="utf-8"
    )
    assert "mcp.sync.missing" in codes(validate.check_mcp(root), "error")


def test_hook_without_exec_bit(tmp_path, repo_root):
    root = make_package(tmp_path, repo_root)
    hook = root / "governance" / "hooks" / "gate.sh"
    hook.write_text("#!/usr/bin/env bash\nset -euo pipefail\nexit 0\n", encoding="utf-8")
    hook.chmod(0o644)
    assert "hooks.exec" in codes(validate.check_hooks(root), "error")


def test_hook_without_strict_mode(tmp_path, repo_root):
    root = make_package(tmp_path, repo_root)
    hook = root / "governance" / "hooks" / "gate.sh"
    hook.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    hook.chmod(0o755)
    assert "hooks.strict" in codes(validate.check_hooks(root), "error")


def test_missing_template(tmp_path, repo_root):
    root = make_package(tmp_path, repo_root)
    (root / "templates" / "05-deploy.md").unlink()
    assert "templates.missing" in codes(validate.check_templates(root), "error")


def test_eval_check_must_be_executable(tmp_path, repo_root):
    root = make_package(tmp_path, repo_root)
    script = root / "evals" / "check.sh"
    script.write_text("#!/usr/bin/env bash\n", encoding="utf-8")
    script.chmod(0o644)
    (root / "evals" / "e.json").write_text(
        json.dumps({"name": "e", "prompt": "p", "check": "evals/check.sh"}), encoding="utf-8"
    )
    assert "evals.check-exec" in codes(validate.check_evals(root), "error")


def test_plan_contract_is_enforced_in_examples(tmp_path, repo_root):
    root = make_package(tmp_path, repo_root)
    folder = root / "examples" / "intents" / "x-20260101"
    folder.mkdir(parents=True)
    (folder / "01-intent.md").write_text("# Intent: x\n", encoding="utf-8")
    (folder / "03-plan.md").write_text("# Plan: x\n\n## Order of work\n\n1. go\n", encoding="utf-8")
    problems = codes(validate.check_examples(root), "error")
    assert "examples.plan-contract" in problems
    assert "examples.chain" in problems  # 02-spec.md is missing, so the chain has a gap


def test_run_all_collects_from_every_check(tmp_path, repo_root):
    """A failing skill must not hide MCP or hook errors the way the old
    short-circuiting validator did."""
    root = make_package(tmp_path, repo_root)
    add_skill(root, "03-thing", front="name: wrong\ndescription: Long enough description. Use when testing.\n")
    (root / "mcp" / "configs" / "svc.json").write_text("{not json", encoding="utf-8")
    found = codes(validate.run_all(root), "error")
    assert "skill.name.mismatch" in found
    assert "mcp.json" in found


def test_documented_flag_that_does_not_exist(tmp_path, repo_root):
    """The same defect class as a documented-but-missing subcommand; it just
    fails later, in a user's terminal."""
    doc = tmp_path / "GUIDE.md"
    doc.write_text("Run `ai-dlc metrics --not-a-real-flag` for details.\n", encoding="utf-8")
    problems = validate._check_documented_flags(tmp_path, [doc], {"metrics"})
    assert [p.code for p in problems] == ["docs.cli-unknown-flag"]
    assert "--not-a-real-flag" in problems[0].message


def test_real_flags_pass(tmp_path):
    doc = tmp_path / "GUIDE.md"
    doc.write_text("Run `ai-dlc backlog --collisions --json` to check.\n", encoding="utf-8")
    assert validate._check_documented_flags(tmp_path, [doc], {"backlog"}) == []


def test_every_subcommand_has_an_introspectable_parser():
    """If a parser cannot be introspected the flag check silently passes, so the
    map must stay complete as subcommands are added."""
    from ai_dlc.cli import build_parser

    registered = set()
    for action in build_parser()._subparsers._group_actions:
        registered.update(getattr(action, "choices", {}) or {})
    assert registered == set(validate.SUBCOMMAND_PARSERS)
    for command in registered:
        assert validate._subcommand_flags(command), command
