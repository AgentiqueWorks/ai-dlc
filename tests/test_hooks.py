"""The governance hooks are the deterministic gates, so they get real tests.

The bug these guard against is subtle: a hook that reads stdin twice gets an
empty string the second time and silently stops gating anything.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

HOOKS = Path(__file__).resolve().parent.parent / "governance" / "hooks"


def run_hook(name: str, payload: dict, tmp_path: Path, env: dict = None):
    if not shutil.which("bash"):
        pytest.skip("bash is not available")
    full_env = {"PATH": "/usr/bin:/bin:/usr/local/bin", "CLAUDE_PROJECT_DIR": str(tmp_path)}
    full_env.update(env or {})
    return subprocess.run(
        ["bash", str(HOOKS / name)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=full_env,
    )


@pytest.mark.parametrize("hook", sorted(p.name for p in HOOKS.glob("*.sh")))
def test_shell_syntax_is_valid(hook):
    assert subprocess.run(["bash", "-n", str(HOOKS / hook)], capture_output=True).returncode == 0


@pytest.mark.parametrize("hook", sorted(p.name for p in HOOKS.glob("*.sh")))
def test_hooks_are_strict_and_executable(hook):
    text = (HOOKS / hook).read_text()
    assert text.startswith("#!"), hook
    assert "set -euo pipefail" in text, hook
    assert (HOOKS / hook).stat().st_mode & 0o111, hook


def test_block_test_edit_blocks_a_test_file(tmp_path):
    result = run_hook(
        "block-test-edit.sh",
        {"tool_name": "Edit", "tool_input": {"file_path": "src/api.test.ts"}},
        tmp_path,
        {"FIX_TASK": "1"},
    )
    assert result.returncode == 2
    assert "test file" in result.stderr


def test_block_test_edit_allows_source(tmp_path):
    result = run_hook(
        "block-test-edit.sh",
        {"tool_name": "Edit", "tool_input": {"file_path": "src/api.ts"}},
        tmp_path,
        {"FIX_TASK": "1"},
    )
    assert result.returncode == 0


def test_block_test_edit_is_inert_without_fix_task(tmp_path):
    result = run_hook(
        "block-test-edit.sh", {"tool_name": "Edit", "tool_input": {"file_path": "src/api.test.ts"}}, tmp_path
    )
    assert result.returncode == 0


def test_migration_requires_a_ticket(tmp_path):
    payload = {"tool_name": "Edit", "tool_input": {"file_path": "db/migrations/003_add.sql"}}
    assert run_hook("migration-ticket.sh", payload, tmp_path).returncode == 2
    assert run_hook("migration-ticket.sh", payload, tmp_path, {"CHANGE_TICKET": "CHG-1"}).returncode == 0


def test_production_gate(tmp_path):
    prod = {"tool_name": "Bash", "tool_input": {"command": "npm run deploy -- --env production"}}
    staging = {"tool_name": "Bash", "tool_input": {"command": "npm run deploy -- --env staging"}}
    assert run_hook("production-gate.sh", prod, tmp_path).returncode == 2
    assert run_hook("production-gate.sh", prod, tmp_path, {"RELEASE_APPROVAL": "REL-1"}).returncode == 0
    assert run_hook("production-gate.sh", staging, tmp_path).returncode == 0


@pytest.mark.parametrize(
    "command,blocked",
    [
        ("gh pr merge 42 --squash", True),
        ("gh pr review 42 --approve", True),
        ("gh pr comment 42 --body findings", False),
        ("git push --force origin main", True),
        ("git push --force origin intent/foo", False),
    ],
)
def test_no_self_approve(command, blocked, tmp_path):
    result = run_hook("no-self-approve.sh", {"tool_name": "Bash", "tool_input": {"command": command}}, tmp_path)
    assert (result.returncode == 2) is blocked, result.stderr


def test_denials_are_audited_under_the_right_hook_name(tmp_path):
    run_hook(
        "production-gate.sh",
        {"tool_name": "Bash", "tool_input": {"command": "deploy to production"}},
        tmp_path,
    )
    log = tmp_path / ".ai-dlc" / "audit.jsonl"
    if not log.is_file():
        pytest.skip("jq is not installed, so the hook could not parse the payload")
    entry = json.loads(log.read_text().splitlines()[-1])
    assert entry["decision"] == "deny"
    assert entry["hook"] == "production-gate.sh"
    assert entry["tool"] == "Bash"
