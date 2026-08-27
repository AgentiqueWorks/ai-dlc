"""The backlog reads intents/ as a work queue, including branch-only intents."""

from __future__ import annotations

import json

import pytest

from ai_dlc import backlog


@pytest.fixture
def queue(git_repo):
    g = git_repo
    g.write("README.md", "# demo\n")
    g.commit("init", "2026-08-01T09:00:00+00:00")

    g.run("switch", "-qc", "intent/alpha-20260801")
    g.write("intents/alpha-20260801/01-intent.md", "# Intent: Alpha\n\n- **Status:** approved\n")
    g.write("intents/alpha-20260801/02-spec.md", "# Spec: Alpha\n\n- **Status:** in-progress\n")
    g.commit("alpha", "2026-08-01T10:00:00+00:00")

    g.run("switch", "-q", "main")
    g.run("switch", "-qc", "intent/beta-20260101")
    g.write("intents/beta-20260101/01-intent.md", "# Intent: Beta\n\n- **Status:** draft\n")
    g.commit("beta", "2026-01-01T10:00:00+00:00")
    g.run("switch", "-q", "main")
    return g


def test_rows_cover_branch_only_intents(queue):
    rows = {r.id: r for r in backlog.build(queue.path)}
    assert set(rows) == {"alpha-20260801", "beta-20260101"}
    assert rows["alpha-20260801"].stage == "02-design"
    assert rows["alpha-20260801"].next_artifact == "03-plan.md"
    assert rows["alpha-20260801"].chain == "●●○○○○"
    assert rows["alpha-20260801"].branch == "intent/alpha-20260801"


def test_status_comes_from_the_highest_artifact(queue):
    rows = {r.id: r for r in backlog.build(queue.path)}
    assert rows["alpha-20260801"].status == "in-progress"


def test_stale_intents_are_flagged(queue):
    rows = {r.id: r for r in backlog.build(queue.path, stale_days=30)}
    assert rows["beta-20260101"].stale is True
    assert rows["beta-20260101"].age_days > 30


def test_titles_are_parsed(queue):
    rows = {r.id: r for r in backlog.build(queue.path)}
    assert rows["alpha-20260801"].title == "Alpha"


def test_json_output(queue, capsys):
    assert backlog.main([str(queue.path), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert {row["id"] for row in payload["intents"]} == {"alpha-20260801", "beta-20260101"}


def test_stage_filter(queue, capsys):
    assert backlog.main([str(queue.path), "--stage", "01"]) == 0
    out = capsys.readouterr().out
    assert "beta-20260101" in out
    assert "alpha-20260801" not in out


def test_no_layout_exits_three(tmp_path):
    assert backlog.main([str(tmp_path)]) == 3


def test_works_without_git(tmp_path):
    folder = tmp_path / "intents" / "gamma-20260101"
    folder.mkdir(parents=True)
    (folder / "01-intent.md").write_text("# Intent: Gamma\n\n- **Status:** draft\n")
    rows = backlog.build(tmp_path, use_git=False)
    assert len(rows) == 1
    assert rows[0].branch is None
    assert rows[0].age_days is None


@pytest.fixture
def colliding(git_repo):
    """Two in-flight intents whose plans claim an overlapping file."""
    g = git_repo
    g.write("README.md", "# demo\n")
    g.commit("init", "2026-08-01T09:00:00+00:00")

    def plan(paths):
        bullets = "\n".join(f"- `{p}`" for p in paths)
        return f"# Plan: x\n\n- **Status:** approved\n\n## Files that change\n\n{bullets}\n"

    for name, paths in (
        ("alpha-20260801", ["src/api/reports.ts", "src/lib/csv.ts"]),
        ("beta-20260801", ["src/api/reports.ts", "src/lib/limits.ts"]),
        ("gamma-20260801", ["src/ui/page.tsx"]),
    ):
        g.run("switch", "-q", "main")
        g.run("switch", "-qc", f"intent/{name}")
        g.write(f"intents/{name}/01-intent.md", f"# Intent: {name}\n\n- **Status:** approved\n")
        g.write(f"intents/{name}/03-plan.md", plan(paths))
        g.commit(name, "2026-08-01T10:00:00+00:00")
    g.run("switch", "-q", "main")
    return g


def test_collisions_are_found_before_any_code_is_written(colliding):
    found = backlog.collisions(colliding.path)
    assert len(found) == 1
    hit = found[0]
    assert {hit.a, hit.b} == {"alpha-20260801", "beta-20260801"}
    assert hit.paths == ("src/api/reports.ts",)


def test_non_overlapping_intents_do_not_collide(colliding):
    found = backlog.collisions(colliding.path)
    assert all("gamma-20260801" not in (c.a, c.b) for c in found)


def test_finished_intents_cannot_collide(git_repo):
    g = git_repo
    g.write("README.md", "# demo\n")
    g.commit("init", "2026-08-01T09:00:00+00:00")
    for name, status in (("alpha-20260801", "done"), ("beta-20260801", "approved")):
        g.run("switch", "-q", "main")
        g.run("switch", "-qc", f"intent/{name}")
        g.write(f"intents/{name}/01-intent.md", f"# Intent: {name}\n")
        g.write(
            f"intents/{name}/03-plan.md",
            f"# Plan: {name}\n\n- **Status:** {status}\n\n## Files that change\n\n- `src/shared.ts`\n",
        )
        g.commit(name, "2026-08-01T10:00:00+00:00")
    g.run("switch", "-q", "main")
    assert backlog.collisions(g.path) == []


def test_collisions_json_output(colliding, capsys):
    assert backlog.main([str(colliding.path), "--collisions", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["collisions"][0]["paths"] == ["src/api/reports.ts"]


def test_collisions_text_output_names_the_remedy(colliding, capsys):
    assert backlog.main([str(colliding.path), "--collisions"]) == 0
    out = capsys.readouterr().out
    assert "alpha-20260801" in out and "beta-20260801" in out
    assert "Sequence these intents" in out
