#!/usr/bin/env python3
"""Compute the locally derivable AI-Native SDLC indicators.

The playbook names roughly thirty leading and lagging indicators. Most need a
PR API, a CI API, or an OpenTelemetry export. A meaningful subset is derivable
from the intents/ tree and local git history alone, and those are the ones this
module implements. ``references/indicators.yaml`` is the single source of truth
for which is which, and ``ai-dlc validate`` enforces that this registry and that
catalog agree -- so an indicator can never quietly claim an implementation it
does not have.

Design rule: when the data is missing or untrustworthy (no git, shallow clone,
no plan section) an indicator reports ``computable: false`` rather than a
plausible-looking wrong number.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from . import gitio, render
from .catalog import load_indicator_catalog
from .repo import ARTIFACTS, Intent, find_root, load_intents

__all__ = ["IndicatorResult", "Report", "REGISTRY", "collect", "render_table", "render_json", "main"]

EXIT_OK = 0
EXIT_THRESHOLD = 1
EXIT_ENVIRONMENT = 3


@dataclass
class IndicatorResult:
    name: str
    scope: str  # "repo" | "intent"
    subject: Optional[str]
    value: Any
    unit: str
    detail: Dict[str, Any] = field(default_factory=dict)
    computable: bool = True
    approximate: bool = False
    note: str = ""


@dataclass
class Report:
    root: Path
    generated_at: datetime
    git: Dict[str, Any]
    warnings: List[str]
    intents: int
    results: List[IndicatorResult]
    documented_only: List[str]

    def by_name(self, name: str) -> List[IndicatorResult]:
        return [r for r in self.results if r.name == name]

    def repo_value(self, name: str) -> Any:
        for r in self.results:
            if r.name == name and r.scope == "repo":
                return r.value
        return None


@dataclass
class Context:
    """Everything the indicator functions need, gathered once."""

    root: Path
    intents: List[Intent]
    git_ok: bool
    shallow: bool
    default_branch: str
    first_add: Dict[str, datetime]
    last_touch: Dict[str, datetime]
    branches: Dict[str, Optional[str]]
    branch_commits: Dict[str, List[gitio.Commit]]
    branch_files: Dict[str, List[str]]
    landed: Dict[str, Optional[datetime]]
    approximate_diff: Dict[str, bool]
    stale_days: int

    def artifact_time(self, intent: Intent, artifact: str) -> Optional[datetime]:
        path = intent.artifacts.get(artifact)
        if not path:
            return None
        rel = f"intents/{intent.id}/{artifact}"
        stamp = self.first_add.get(rel)
        if stamp is None and path.is_file():
            return None
        return stamp

    def last_activity(self, intent: Intent) -> Optional[datetime]:
        prefix = f"intents/{intent.id}/"
        stamps = [v for k, v in self.last_touch.items() if k.startswith(prefix)]
        return max(stamps) if stamps else None


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def _delta_seconds(start: Optional[datetime], end: Optional[datetime]) -> Optional[float]:
    if start is None or end is None:
        return None
    seconds = (_aware(end) - _aware(start)).total_seconds()
    return seconds if seconds >= 0 else None


def _median(values: List[float]) -> Optional[float]:
    return statistics.median(values) if values else None


# ---------------------------------------------------------------- indicators


def indicator_artifact_chain_completeness(ctx: Context) -> List[IndicatorResult]:
    results: List[IndicatorResult] = []
    total_present = 0
    total_slots = 0
    for intent in ctx.intents:
        present = len(intent.artifacts)
        total_present += present
        total_slots += len(ARTIFACTS)
        results.append(
            IndicatorResult(
                name="artifact-chain-completeness",
                scope="intent",
                subject=intent.id,
                value=present / len(ARTIFACTS),
                unit="ratio",
                detail={
                    "present": present,
                    "of": len(ARTIFACTS),
                    "chain": intent.chain,
                    "missing": [a for a in ARTIFACTS if a not in intent.artifacts],
                },
            )
        )
    repo_value = (total_present / total_slots) if total_slots else None
    results.insert(
        0,
        IndicatorResult(
            name="artifact-chain-completeness",
            scope="repo",
            subject=None,
            value=repo_value,
            unit="ratio",
            detail={"present": total_present, "of": total_slots, "intents": len(ctx.intents)},
            computable=bool(ctx.intents),
            note="" if ctx.intents else "no intents found",
        ),
    )
    return results


_LATENCY_PAIRS = (
    ("intent->spec", "01-intent.md", "02-spec.md"),
    ("spec->plan", "02-spec.md", "03-plan.md"),
    ("plan->review", "03-plan.md", "04-review.md"),
    ("review->deploy", "04-review.md", "05-deploy.md"),
)


def indicator_stage_latency(ctx: Context) -> List[IndicatorResult]:
    if not ctx.git_ok or ctx.shallow:
        return [
            IndicatorResult(
                "stage-latency", "repo", None, None, "duration",
                computable=False,
                note="shallow clone" if ctx.shallow else "not a git repository",
            )
        ]
    results: List[IndicatorResult] = []
    for label, first, second in _LATENCY_PAIRS:
        samples: List[float] = []
        per_intent: Dict[str, float] = {}
        for intent in ctx.intents:
            delta = _delta_seconds(ctx.artifact_time(intent, first), ctx.artifact_time(intent, second))
            if delta is not None:
                samples.append(delta)
                per_intent[intent.id] = delta
        results.append(
            IndicatorResult(
                name="stage-latency",
                scope="repo",
                subject=label,
                value=_median(samples),
                unit="duration",
                detail={
                    "n": len(samples),
                    "min": min(samples) if samples else None,
                    "max": max(samples) if samples else None,
                    "per_intent": per_intent,
                },
                computable=bool(samples),
                note="" if samples else "no intent has both artifacts in history",
            )
        )
    # intent -> landed on the default branch
    landed_samples: List[float] = []
    for intent in ctx.intents:
        delta = _delta_seconds(ctx.artifact_time(intent, "01-intent.md"), ctx.landed.get(intent.id))
        if delta is not None:
            landed_samples.append(delta)
    results.append(
        IndicatorResult(
            name="stage-latency",
            scope="repo",
            subject="intent->landed",
            value=_median(landed_samples),
            unit="duration",
            detail={"n": len(landed_samples)},
            computable=bool(landed_samples),
            note="" if landed_samples else "no intent has landed on the default branch",
        )
    )
    return results


def indicator_time_to_intent(ctx: Context) -> List[IndicatorResult]:
    samples: List[float] = []
    carrying = 0
    for intent in ctx.intents:
        if intent.signal_at is None:
            continue
        carrying += 1
        delta = _delta_seconds(intent.signal_at, ctx.artifact_time(intent, "01-intent.md"))
        if delta is not None:
            samples.append(delta)
    note = ""
    if not carrying:
        note = "no intent declares '- **Signal at:**'; add it to templates/01-intent.md"
    elif not ctx.git_ok:
        note = "not a git repository"
    return [
        IndicatorResult(
            name="time-to-intent",
            scope="repo",
            subject=None,
            value=_median(samples),
            unit="duration",
            detail={"n": len(samples), "carrying_field": carrying, "of": len(ctx.intents)},
            computable=bool(samples),
            note=note,
        )
    ]


def indicator_intent_survival(ctx: Context) -> List[IndicatorResult]:
    if not ctx.git_ok or ctx.shallow:
        return [
            IndicatorResult(
                "intent-survival", "repo", None, None, "ratio",
                computable=False,
                note="shallow clone" if ctx.shallow else "not a git repository",
            )
        ]
    landed = [i.id for i in ctx.intents if ctx.landed.get(i.id)]
    open_ids: List[str] = []
    stale_ids: List[str] = []
    cutoff = _now() - timedelta(days=ctx.stale_days)
    for intent in ctx.intents:
        if ctx.landed.get(intent.id):
            continue
        activity = ctx.last_activity(intent)
        if activity and _aware(activity) < cutoff:
            stale_ids.append(intent.id)
        else:
            open_ids.append(intent.id)
    total = len(ctx.intents)
    return [
        IndicatorResult(
            name="intent-survival",
            scope="repo",
            subject=None,
            value=(len(landed) / total) if total else None,
            unit="ratio",
            detail={"landed": landed, "open": open_ids, "stale": stale_ids},
            computable=bool(total),
            approximate=True,
            note=(
                "It counts an intent as landed when 01-intent.md reaches the default branch. "
                "A team that squash-merges and deletes branches without landing intents/ will read 0% "
                "while shipping normally, so check the merge strategy before reading this as a delivery problem."
            ),
        )
    ]


def indicator_intent_staleness(ctx: Context) -> List[IndicatorResult]:
    if not ctx.git_ok:
        return [IndicatorResult("intent-staleness", "repo", None, None, "count", computable=False, note="not a git repository")]
    cutoff = _now() - timedelta(days=ctx.stale_days)
    stale: Dict[str, int] = {}
    for intent in ctx.intents:
        if ctx.landed.get(intent.id):
            continue
        activity = ctx.last_activity(intent)
        if activity and _aware(activity) < cutoff:
            stale[intent.id] = (_now() - _aware(activity)).days
    return [
        IndicatorResult(
            name="intent-staleness",
            scope="repo",
            subject=None,
            value=len(stale),
            unit="count",
            detail={"stale_days": ctx.stale_days, "intents": stale},
        )
    ]


def indicator_spec_churn(ctx: Context) -> List[IndicatorResult]:
    if not ctx.git_ok or ctx.shallow:
        return [
            IndicatorResult(
                "spec-churn", "repo", None, None, "count",
                computable=False,
                note="shallow clone" if ctx.shallow else "not a git repository",
            )
        ]
    per_intent: Dict[str, int] = {}
    for intent in ctx.intents:
        plan_time = ctx.artifact_time(intent, "03-plan.md")
        if plan_time is None or "02-spec.md" not in intent.artifacts:
            continue
        rel = f"intents/{intent.id}/02-spec.md"
        count = 0
        for commit in ctx.branch_commits.get(intent.id, []):
            if rel in commit.files and _aware(commit.authored_at) > _aware(plan_time):
                count += 1
        per_intent[intent.id] = count
    values = list(per_intent.values())
    return [
        IndicatorResult(
            name="spec-churn",
            scope="repo",
            subject=None,
            value=_median([float(v) for v in values]),
            unit="count",
            detail={"n": len(values), "total": sum(values), "per_intent": per_intent},
            computable=bool(values),
            note="" if values else "no intent has both a spec and a plan in history",
        )
    ]


def _normalize(path: str) -> str:
    return path.strip().lstrip("./")


def indicator_plan_diff_alignment(ctx: Context) -> List[IndicatorResult]:
    if not ctx.git_ok or ctx.shallow:
        return [
            IndicatorResult(
                "plan-diff-alignment", "repo", None, None, "ratio",
                computable=False,
                note="shallow clone" if ctx.shallow else "not a git repository",
            )
        ]
    results: List[IndicatorResult] = []
    skipped: List[str] = []
    total_planned = 0
    total_matched = 0
    total_unplanned = 0
    for intent in ctx.intents:
        if "03-plan.md" not in intent.artifacts:
            continue
        if not intent.planned_files:
            skipped.append(intent.id)
            continue
        changed = {_normalize(p) for p in ctx.branch_files.get(intent.id, []) if not p.startswith("intents/")}
        if not changed:
            skipped.append(intent.id)
            continue
        planned = {_normalize(p) for p in intent.planned_files}
        matched = {p for p in planned if p in changed or any(c.startswith(p.rstrip("/") + "/") for c in changed)}
        unplanned = {c for c in changed if c not in planned and not any(c.startswith(p.rstrip("/") + "/") for p in planned)}
        total_planned += len(planned)
        total_matched += len(matched)
        total_unplanned += len(unplanned)
        denominator = len(planned | unplanned)
        results.append(
            IndicatorResult(
                name="plan-diff-alignment",
                scope="intent",
                subject=intent.id,
                value=(len(matched) / denominator) if denominator else None,
                unit="ratio",
                detail={
                    "planned": len(planned),
                    "matched": len(matched),
                    "unplanned": sorted(unplanned),
                    "missed": sorted(planned - matched),
                },
                approximate=ctx.approximate_diff.get(intent.id, False),
            )
        )
    denominator = total_planned + total_unplanned
    results.insert(
        0,
        IndicatorResult(
            name="plan-diff-alignment",
            scope="repo",
            subject=None,
            value=(total_matched / denominator) if denominator else None,
            unit="ratio",
            detail={
                "planned": total_planned,
                "matched": total_matched,
                "unplanned": total_unplanned,
                "skipped": skipped,
            },
            computable=bool(denominator),
            note="" if denominator else "no plan lists files under '## Files that change'",
        ),
    )
    return results


def indicator_rework_after_review(ctx: Context) -> List[IndicatorResult]:
    if not ctx.git_ok or ctx.shallow:
        return [
            IndicatorResult(
                "rework-after-review", "repo", None, None, "count",
                computable=False,
                note="shallow clone" if ctx.shallow else "not a git repository",
            )
        ]
    per_intent: Dict[str, int] = {}
    for intent in ctx.intents:
        review_time = ctx.artifact_time(intent, "04-review.md")
        if review_time is None:
            continue
        count = 0
        for commit in ctx.branch_commits.get(intent.id, []):
            if _aware(commit.authored_at) <= _aware(review_time):
                continue
            if any(not f.startswith("intents/") for f in commit.files):
                count += 1
        per_intent[intent.id] = count
    values = [float(v) for v in per_intent.values()]
    return [
        IndicatorResult(
            name="rework-after-review",
            scope="repo",
            subject=None,
            value=_median(values),
            unit="count",
            detail={"n": len(values), "per_intent": per_intent},
            computable=bool(values),
            note="" if values else "no intent has a committed 04-review.md",
        )
    ]


REGISTRY: Dict[str, Callable[[Context], List[IndicatorResult]]] = {
    "artifact-chain-completeness": indicator_artifact_chain_completeness,
    "time-to-intent": indicator_time_to_intent,
    "intent-survival": indicator_intent_survival,
    "intent-staleness": indicator_intent_staleness,
    "stage-latency": indicator_stage_latency,
    "spec-churn": indicator_spec_churn,
    "plan-diff-alignment": indicator_plan_diff_alignment,
    "rework-after-review": indicator_rework_after_review,
}


# ------------------------------------------------------------------- collect


def _build_context(root: Path, stale_days: int) -> tuple[Context, List[str]]:
    warnings: List[str] = []
    intents = load_intents(root)
    git_ok = gitio.git_available() and gitio.repo_root(root) is not None
    shallow = git_ok and gitio.is_shallow(root)
    if not gitio.git_available():
        warnings.append("git is not installed; history-derived indicators are unavailable")
    elif not git_ok:
        warnings.append("not inside a git repository; history-derived indicators are unavailable")
    if shallow:
        warnings.append(
            "shallow clone detected; history-derived indicators are suppressed. "
            "Use actions/checkout with fetch-depth: 0"
        )

    first_add: Dict[str, datetime] = {}
    last_touch: Dict[str, datetime] = {}
    branches: Dict[str, Optional[str]] = {}
    branch_commits: Dict[str, List[gitio.Commit]] = {}
    branch_files: Dict[str, List[str]] = {}
    landed: Dict[str, Optional[datetime]] = {}
    approximate_diff: Dict[str, bool] = {}
    default = ""

    if git_ok and not shallow:
        first_add = gitio.first_add_times(root, "intents/")
        last_touch = gitio.last_touch_times(root, "intents/")
        default = gitio.default_branch(root)
        for intent in intents:
            landed[intent.id] = gitio.landed_time(root, default, f"intents/{intent.id}/01-intent.md")
            branch = gitio.branch_for_intent(root, intent.id)
            branches[intent.id] = branch
            if branch:
                base = gitio.merge_base(root, default, branch)
                if base:
                    branch_commits[intent.id] = gitio.commits_since(root, base, branch)
                    branch_files[intent.id] = gitio.changed_files(root, base, branch)
                    approximate_diff[intent.id] = False
                    continue
            # Branch is gone (squash-merged and deleted). Fall back to the
            # default-branch commits that touched this intent's folder, which is
            # exactly right for a squash merge and undercounts a merge commit.
            commits = [
                c
                for c in gitio.commits_since(root, f"{default}~200", default)
                if any(f.startswith(f"intents/{intent.id}/") for f in c.files)
            ]
            branch_commits[intent.id] = commits
            branch_files[intent.id] = sorted({f for c in commits for f in c.files})
            approximate_diff[intent.id] = True

    ctx = Context(
        root=root,
        intents=intents,
        git_ok=git_ok and not shallow,
        shallow=shallow,
        default_branch=default,
        first_add=first_add,
        last_touch=last_touch,
        branches=branches,
        branch_commits=branch_commits,
        branch_files=branch_files,
        landed=landed,
        approximate_diff=approximate_diff,
        stale_days=stale_days,
    )
    return ctx, warnings


def collect(
    root: Path,
    only: Optional[List[str]] = None,
    stale_days: int = 30,
    intent: Optional[str] = None,
) -> Report:
    root = Path(root).expanduser().resolve()
    ctx, warnings = _build_context(root, stale_days)
    if intent:
        ctx.intents = [i for i in ctx.intents if i.id == intent]

    names = list(REGISTRY) if not only else [n for n in REGISTRY if n in set(only)]
    results: List[IndicatorResult] = []
    for name in names:
        results.extend(REGISTRY[name](ctx))

    catalog = load_indicator_catalog()
    documented = sorted(n for n, spec in catalog.items() if spec.get("computable") == "external")

    return Report(
        root=root,
        generated_at=_now(),
        git={
            "available": gitio.git_available(),
            "repository": gitio.repo_root(root) is not None if gitio.git_available() else False,
            "shallow": ctx.shallow,
            "default_branch": ctx.default_branch or None,
        },
        warnings=warnings,
        intents=len(ctx.intents),
        results=results,
        documented_only=documented,
    )


# ------------------------------------------------------------------ renderers


def render_table(report: Report) -> str:
    lines: List[str] = []
    git_state = "no git"
    if report.git["repository"]:
        git_state = "shallow history" if report.git["shallow"] else "full history"
    lines.append(f"AI-DLC metrics — {report.root}")
    lines.append(
        f"{report.intents} intent(s) · {git_state}"
        + (f" · default branch {report.git['default_branch']}" if report.git.get("default_branch") else "")
    )
    lines.append("")

    rows: List[List[str]] = []
    for result in report.results:
        if result.scope != "repo":
            continue
        label = result.name + (f":{result.subject}" if result.subject else "")
        if result.approximate:
            label += " ~"
        value = render.fmt_value(result.value, result.unit) if result.computable else "n/a"
        detail = _detail_line(result)
        rows.append([label, value, detail])
    lines.append(render.table(["INDICATOR", "VALUE", "DETAIL"], rows))

    per_intent = [r for r in report.results if r.scope == "intent"]
    if per_intent:
        lines.append("")
        lines.append("Per intent")
        rows = []
        for result in per_intent:
            rows.append(
                [
                    result.subject or "",
                    result.name,
                    render.fmt_value(result.value, result.unit) if result.computable else "n/a",
                    _detail_line(result),
                ]
            )
        lines.append(render.table(["INTENT", "INDICATOR", "VALUE", "DETAIL"], rows))

    footnotes = [r for r in report.results if r.approximate and r.note and r.scope == "repo"]
    if footnotes:
        lines.append("")
        for result in footnotes:
            label = result.name + (f":{result.subject}" if result.subject else "")
            lines.append(f"~ {label} is approximate. {result.note}")

    if report.warnings:
        lines.append("")
        for warning in report.warnings:
            lines.append(f"warning: {warning}")

    if report.documented_only:
        lines.append("")
        lines.append("Documented only (needs an external API): " + ", ".join(report.documented_only))
        lines.append("See references/metrics-catalog.md for how to wire each one up.")
    return "\n".join(lines)


def _detail_line(result: IndicatorResult) -> str:
    if not result.computable and result.note:
        return result.note
    detail = result.detail
    if result.name == "artifact-chain-completeness":
        if result.scope == "repo":
            return f"{detail.get('present')}/{detail.get('of')} artifacts"
        return str(detail.get("chain", ""))
    if result.name == "plan-diff-alignment":
        if result.scope == "repo":
            return (
                f"planned {detail.get('planned')} · matched {detail.get('matched')} · "
                f"unplanned {detail.get('unplanned')}"
            )
        return f"matched {detail.get('matched')}/{detail.get('planned')} · unplanned {len(detail.get('unplanned', []))}"
    if result.name == "stage-latency":
        n = detail.get("n", 0)
        if not n:
            return result.note
        return f"n={n} min {render.fmt_duration(detail.get('min'))} max {render.fmt_duration(detail.get('max'))}"
    if result.name == "intent-survival":
        return (
            f"{len(detail.get('landed', []))} landed · {len(detail.get('open', []))} open · "
            f"{len(detail.get('stale', []))} stale"
        )
    if result.name == "intent-staleness":
        names = ", ".join(f"{k} ({v}d)" for k, v in detail.get("intents", {}).items())
        return names or f"none over {detail.get('stale_days')}d"
    if result.name == "time-to-intent":
        return result.note or f"n={detail.get('n')} of {detail.get('of')} intents"
    if result.name in ("spec-churn", "rework-after-review"):
        return result.note or f"n={detail.get('n')}"
    return result.note


def render_json(report: Report) -> str:
    payload = {
        "schema": 1,
        "root": str(report.root),
        "generated_at": report.generated_at.isoformat(),
        "git": report.git,
        "warnings": report.warnings,
        "intents": report.intents,
        "documented_only": report.documented_only,
        "indicators": [asdict(r) for r in report.results],
    }
    return json.dumps(payload, indent=2, default=str)


def render_markdown(report: Report) -> str:
    rows = []
    for result in report.results:
        if result.scope != "repo":
            continue
        label = result.name + (f":{result.subject}" if result.subject else "")
        rows.append(
            [
                label,
                render.fmt_value(result.value, result.unit) if result.computable else "n/a",
                _detail_line(result).replace("|", "\\|"),
            ]
        )
    return "\n".join(
        [
            f"## AI-DLC metrics",
            "",
            f"`{report.root}` · {report.intents} intent(s)",
            "",
            render.markdown_table(["Indicator", "Value", "Detail"], rows),
        ]
        + (
            [""]
            + [
                f"`{r.name}` is approximate. {r.note}"
                for r in report.results
                if r.approximate and r.note and r.scope == "repo"
            ]
            if any(r.approximate and r.note and r.scope == "repo" for r in report.results)
            else []
        )
    )


# ------------------------------------------------------------------------ CLI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-dlc metrics", description="Compute AI-DLC delivery indicators")
    parser.add_argument("path", nargs="?", default=".", help="Path inside an AI-DLC project")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--markdown", action="store_true", help="Emit a Markdown table for a PR comment")
    parser.add_argument("--indicator", action="append", dest="indicators", help="Limit to one indicator (repeatable)")
    parser.add_argument("--list-indicators", action="store_true", help="List every indicator and its computability")
    parser.add_argument("--intent", help="Limit to a single intent id")
    parser.add_argument("--stale-days", type=int, default=30, help="Days of inactivity before an intent is stale")
    parser.add_argument("--fail-under-completeness", type=float, help="Exit 1 if chain completeness is below this ratio")
    parser.add_argument("--fail-under-alignment", type=float, help="Exit 1 if plan-diff alignment is below this ratio")
    return parser


def _list_indicators() -> int:
    catalog = load_indicator_catalog()
    rows = []
    for name in sorted(catalog):
        spec = catalog[name]
        rows.append(
            [
                name,
                str(spec.get("stage", "")),
                str(spec.get("type", "")),
                str(spec.get("computable", "")),
                "yes" if name in REGISTRY else "no",
            ]
        )
    print(render.table(["INDICATOR", "STAGE", "TYPE", "COMPUTABLE", "IMPLEMENTED"], rows))
    return EXIT_OK


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    if args.list_indicators:
        return _list_indicators()

    start = Path(args.path).expanduser().resolve()
    root = find_root(start)
    if root is None:
        message = "no AI-DLC layout found (expected an intents/ directory). Run `ai-dlc init-repo .` first."
        if args.json:
            print(json.dumps({"schema": 1, "root": str(start), "intents": 0, "error": message}, indent=2))
        else:
            print(message, file=sys.stderr)
        return EXIT_ENVIRONMENT

    report = collect(root, only=args.indicators, stale_days=args.stale_days, intent=args.intent)

    if report.intents == 0 and not (root / "intents").is_dir():
        message = "no AI-DLC layout found (expected an intents/ directory). Run `ai-dlc init-repo .` first."
        if args.json:
            print(json.dumps({"schema": 1, "root": str(root), "intents": 0, "error": message}, indent=2))
        else:
            print(message, file=sys.stderr)
        return EXIT_ENVIRONMENT

    if args.json:
        print(render_json(report))
    elif args.markdown:
        print(render_markdown(report))
    else:
        print(render_table(report))

    status = EXIT_OK
    if args.fail_under_completeness is not None:
        value = report.repo_value("artifact-chain-completeness")
        if value is not None and value < args.fail_under_completeness:
            print(
                f"FAIL: artifact-chain-completeness {value:.2f} < {args.fail_under_completeness:.2f}",
                file=sys.stderr,
            )
            status = EXIT_THRESHOLD
    if args.fail_under_alignment is not None:
        value = report.repo_value("plan-diff-alignment")
        if value is not None and value < args.fail_under_alignment:
            print(f"FAIL: plan-diff-alignment {value:.2f} < {args.fail_under_alignment:.2f}", file=sys.stderr)
            status = EXIT_THRESHOLD
    return status


if __name__ == "__main__":
    sys.exit(main())
