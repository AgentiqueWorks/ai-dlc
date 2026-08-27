"""Metrics are computed against a real git repository with pinned dates."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_dlc import metrics
from ai_dlc.repo import load_intents

PLAN = """# Plan: CSV export

- **Status:** approved

## Files that change

- `src/export.ts`
- `src/routes.ts`
"""


@pytest.fixture
def chain(git_repo):
    """One intent with a full chain on its own branch, plus one stale intent."""
    g = git_repo
    g.write("README.md", "# demo\n")
    g.commit("init", "2026-08-01T09:00:00+00:00")

    g.run("switch", "-qc", "intent/csv-export-20260801")
    g.write(
        "intents/csv-export-20260801/01-intent.md",
        "# Intent: CSV export\n\n- **Status:** approved\n- **Signal at:** 2026-08-01T08:00:00Z\n",
    )
    g.commit("intent", "2026-08-01T10:00:00+00:00")
    g.write("intents/csv-export-20260801/02-spec.md", "# Spec: CSV export\n\n- **Status:** approved\n")
    g.commit("spec", "2026-08-02T10:00:00+00:00")
    g.write("intents/csv-export-20260801/03-plan.md", PLAN)
    g.commit("plan", "2026-08-03T10:00:00+00:00")
    g.write("src/export.ts", "export const a = 1\n")
    g.write("src/routes.ts", "// routes\n")
    g.write("src/unplanned.ts", "// not in the plan\n")
    g.commit("code", "2026-08-03T14:00:00+00:00")
    g.write("intents/csv-export-20260801/04-review.md", "# Review: CSV export\n\n- **Status:** in-review\n")
    g.commit("review", "2026-08-04T10:00:00+00:00")
    g.write("src/export.ts", "export const a = 2\n")
    g.commit("rework", "2026-08-04T15:00:00+00:00")

    g.run("switch", "-q", "main")
    g.run("switch", "-qc", "intent/payment-audit-20260610")
    g.write("intents/payment-audit-20260610/01-intent.md", "# Intent: Payment audit\n\n- **Status:** draft\n")
    g.commit("intent2", "2026-06-10T10:00:00+00:00")
    g.run("switch", "-q", "main")
    return g


def test_intents_on_unmerged_branches_are_visible(chain):
    """One branch per intent means the backlog lives on branches, not on main."""
    intents = load_intents(chain.path)
    assert [i.id for i in intents] == ["csv-export-20260801", "payment-audit-20260610"]
    assert intents[0].ref == "intent/csv-export-20260801"
    assert intents[0].planned_files == ("src/export.ts", "src/routes.ts")


def test_artifact_chain_completeness(chain):
    report = metrics.collect(chain.path)
    assert report.repo_value("artifact-chain-completeness") == pytest.approx(5 / 12)


def test_stage_latency_is_exact(chain):
    report = metrics.collect(chain.path)
    values = {r.subject: r.value for r in report.by_name("stage-latency")}
    assert values["intent->spec"] == pytest.approx(24 * 3600)
    assert values["spec->plan"] == pytest.approx(24 * 3600)
    assert values["plan->review"] == pytest.approx(24 * 3600)


def test_time_to_intent_uses_the_signal_field(chain):
    report = metrics.collect(chain.path)
    result = report.by_name("time-to-intent")[0]
    assert result.value == pytest.approx(2 * 3600)
    assert result.detail["carrying_field"] == 1


def test_plan_diff_alignment_counts_the_unplanned_file(chain):
    report = metrics.collect(chain.path)
    repo_result = [r for r in report.by_name("plan-diff-alignment") if r.scope == "repo"][0]
    assert repo_result.detail == {
        "planned": 2,
        "matched": 2,
        "unplanned": 1,
        "skipped": [],
    }
    assert repo_result.value == pytest.approx(2 / 3)


def test_rework_after_review_counts_only_code_commits(chain):
    report = metrics.collect(chain.path)
    assert report.by_name("rework-after-review")[0].value == pytest.approx(1)


def test_intent_staleness(chain):
    report = metrics.collect(chain.path, stale_days=30)
    result = report.by_name("intent-staleness")[0]
    assert result.value == 1
    assert "payment-audit-20260610" in result.detail["intents"]


def test_survival_is_flagged_approximate(chain):
    report = metrics.collect(chain.path)
    result = report.by_name("intent-survival")[0]
    assert result.approximate is True
    assert result.value == pytest.approx(0.0)


def test_landed_intent_counts_as_survived(chain):
    chain.run("merge", "--no-ff", "-m", "merge", "intent/csv-export-20260801", when="2026-08-05T10:00:00+00:00")
    report = metrics.collect(chain.path)
    assert report.by_name("intent-survival")[0].value == pytest.approx(0.5)


def test_no_git_degrades_instead_of_crashing(tmp_path):
    (tmp_path / "intents" / "a-20260101").mkdir(parents=True)
    (tmp_path / "intents" / "a-20260101" / "01-intent.md").write_text("# Intent: a\n")
    report = metrics.collect(tmp_path)
    assert report.repo_value("artifact-chain-completeness") == pytest.approx(1 / 6)
    history = [r for r in report.by_name("plan-diff-alignment")]
    assert history[0].computable is False


def test_json_output_is_wellformed(chain):
    payload = json.loads(metrics.render_json(metrics.collect(chain.path)))
    assert payload["schema"] == 1
    assert payload["git"]["shallow"] is False
    assert any(i["name"] == "plan-diff-alignment" for i in payload["indicators"])


def test_missing_layout_exits_three(tmp_path, capsys):
    assert metrics.main([str(tmp_path)]) == 3


def test_threshold_failure_exits_one(chain):
    assert metrics.main([str(chain.path), "--fail-under-alignment", "0.9"]) == 1
    assert metrics.main([str(chain.path), "--fail-under-alignment", "0.5"]) == 0


def test_registry_matches_catalog():
    """An indicator can never claim an implementation it does not have."""
    from ai_dlc.catalog import load_indicator_catalog

    catalog = load_indicator_catalog()
    local = {n for n, spec in catalog.items() if spec["computable"] != "external"}
    assert set(metrics.REGISTRY) == local


def test_approximate_caveat_reaches_the_rendered_report(chain):
    """A 0% survival reading must carry its explanation into the output a team
    actually reads, not only into the skill documentation."""
    text = metrics.render_table(metrics.collect(chain.path))
    assert "intent-survival ~" in text
    assert "~ intent-survival is approximate." in text
    assert "squash-merges" in text


def test_approximate_caveat_survives_markdown_output(chain):
    text = metrics.render_markdown(metrics.collect(chain.path))
    assert "`intent-survival` is approximate." in text


def test_shallow_clone_suppresses_history_indicators(chain, tmp_path):
    """A depth-1 clone must produce n/a, never a confident wrong number."""
    import subprocess

    clone = tmp_path / "shallow"
    result = subprocess.run(
        ["git", "clone", "--depth", "1", "file://" + str(chain.path), str(clone)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.skip(f"shallow clone unavailable: {result.stderr.strip()}")

    report = metrics.collect(clone)
    assert any("shallow" in w for w in report.warnings)
    for name in ("stage-latency", "plan-diff-alignment", "rework-after-review"):
        assert all(not r.computable for r in report.by_name(name)), name
