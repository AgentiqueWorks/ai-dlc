"""Scaffolding is additive; migration never destroys content."""

from __future__ import annotations

import json

from ai_dlc import scaffold


def test_creates_layout_v2(tmp_path):
    target = tmp_path / "app"
    scaffold.scaffold(target)
    assert (target / "intents" / "README.md").is_file()
    assert (target / "templates" / "05-deploy.md").is_file()
    assert (target / ".claude" / "hooks" / "production-gate.sh").is_file()
    assert (target / ".claude" / "agents" / "verifier.md").is_file()
    assert (target / "REVIEW.md").is_file()
    assert (target / "bands.yaml").is_file()
    marker = json.loads((target / ".ai-dlc" / "layout.json").read_text().split("\n", 2)[2])
    assert marker["layout_version"] == scaffold.LAYOUT_VERSION
    assert not (target / "intent").exists(), "the flat v1 layout must not be created"


def test_hooks_are_executable(tmp_path):
    target = tmp_path / "app"
    scaffold.scaffold(target)
    hook = target / ".claude" / "hooks" / "production-gate.sh"
    assert hook.stat().st_mode & 0o111


def test_does_not_clobber_existing_files(tmp_path):
    target = tmp_path / "app"
    (target / ".claude" / "skills" / "my-own-skill").mkdir(parents=True)
    (target / ".claude" / "skills" / "my-own-skill" / "SKILL.md").write_text("mine\n")
    (target / "CLAUDE.md").write_text("my own context\n")

    scaffold.scaffold(target)

    assert (target / "CLAUDE.md").read_text() == "my own context\n"
    assert (target / ".claude" / "skills" / "my-own-skill" / "SKILL.md").read_text() == "mine\n"
    assert (target / ".claude" / "skills" / "01-intent-capture" / "SKILL.md").is_file()


def test_is_idempotent(tmp_path):
    target = tmp_path / "app"
    scaffold.scaffold(target)
    second = scaffold.scaffold(target)
    written = [a for a in second if a.kind in ("create", "copy")]
    assert [a.dst.name for a in written] == ["layout.json"]


def test_dry_run_writes_nothing(tmp_path):
    target = tmp_path / "app"
    actions = scaffold.scaffold(target, dry_run=True)
    assert actions
    assert not (target / "intents").exists() or not any((target / "intents").iterdir())


def test_detects_the_old_flat_layout(tmp_path):
    target = tmp_path / "old"
    (target / "intent").mkdir(parents=True)
    (target / "intent" / "csv-export.md").write_text("# Intent: CSV\n")
    assert scaffold.detect_layout(target) == 1


def test_migration_moves_without_losing_content(tmp_path):
    target = tmp_path / "old"
    for directory, name in (("intent", "01"), ("spec", "02"), ("plan", "03")):
        (target / directory).mkdir(parents=True)
        (target / directory / "csv-export.md").write_text(f"# {name}\n")

    actions = scaffold.plan_migration(target)
    scaffold.apply_migration(actions, target, use_git=False)

    folder = target / "intents" / "csv-export"
    assert (folder / "01-intent.md").read_text() == "# 01\n"
    assert (folder / "02-spec.md").read_text() == "# 02\n"
    assert (folder / "03-plan.md").read_text() == "# 03\n"
    assert not (target / "intent").exists()
    assert scaffold.detect_layout(target) == 2


def test_migration_dry_run_is_the_default(tmp_path, capsys):
    target = tmp_path / "old"
    (target / "intent").mkdir(parents=True)
    (target / "intent" / "a.md").write_text("# a\n")
    assert scaffold.migrate_main([str(target)]) == 0
    assert (target / "intent" / "a.md").is_file(), "a dry run must not move anything"


def test_migrating_a_current_project_is_a_noop(tmp_path):
    target = tmp_path / "app"
    scaffold.scaffold(target)
    assert scaffold.migrate_main([str(target)]) == 0
    assert scaffold.plan_migration(target) == []


def test_detects_a_vendored_templates_directory_as_v1(tmp_path):
    """A project can be on intents/<id>/ and still carry pre-0.3.0 template
    names, which is exactly the vendored case the rename breaks."""
    target = tmp_path / "app"
    (target / "intents").mkdir(parents=True)
    (target / "templates").mkdir()
    (target / "templates" / "intent.md").write_text("# Intent: <short title>\n")
    assert scaffold.detect_layout(target) == 1


def test_migration_renames_vendored_templates(tmp_path):
    target = tmp_path / "app"
    (target / "intents").mkdir(parents=True)
    (target / "templates").mkdir()
    (target / "templates" / "intent.md").write_text("# my customized intent\n")
    (target / "templates" / "spec.md").write_text("# my customized spec\n")

    actions = scaffold.plan_migration(target)
    scaffold.apply_migration(actions, target, use_git=False)

    assert (target / "templates" / "01-intent.md").read_text() == "# my customized intent\n"
    assert (target / "templates" / "02-spec.md").read_text() == "# my customized spec\n"
    assert not (target / "templates" / "intent.md").exists()
    # Templates the chain gained in 0.3.0 are added, not invented on the fly.
    assert (target / "templates" / "05-deploy.md").is_file()
    assert scaffold.detect_layout(target) == 2


def test_migration_does_not_overwrite_an_existing_new_name(tmp_path):
    target = tmp_path / "app"
    (target / "intents").mkdir(parents=True)
    (target / "templates").mkdir()
    (target / "templates" / "intent.md").write_text("old\n")
    (target / "templates" / "01-intent.md").write_text("already migrated\n")

    actions = scaffold.plan_migration(target)
    scaffold.apply_migration(actions, target, use_git=False)

    assert (target / "templates" / "01-intent.md").read_text() == "already migrated\n"
    assert (target / "templates" / "intent.md").read_text() == "old\n"


def test_customized_root_artifacts_are_never_moved(tmp_path):
    """A root intent.md the user edited is their content, not our template."""
    target = tmp_path / "app"
    target.mkdir()
    (target / "intent.md").write_text("# Intent: something the user wrote\n")

    actions = scaffold.plan_migration(target)
    scaffold.apply_migration(actions, target, use_git=False)

    assert (target / "intent.md").read_text() == "# Intent: something the user wrote\n"
    assert any(a.kind == "skip" and "modified by you" in a.reason for a in actions)
