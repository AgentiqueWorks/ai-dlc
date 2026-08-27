#!/usr/bin/env python3
"""Render the play dependency graph and the rollout order.

The playbook is explicit that some plays have no prerequisites and others do,
and that adopting them out of order wastes effort. The graph lives in each
skill's ``metadata.requires`` -- one source of truth -- and this module derives
the tiers, the reverse edges, and the suggested order from it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

from . import render
from .yamlite import parse, split_frontmatter

__all__ = ["load_graph", "tiers", "main"]

PACKAGE_ROOT = Path(__file__).resolve().parent.parent


def load_graph(root: Path = PACKAGE_ROOT) -> Dict[str, dict]:
    """Read every skill's frontmatter into ``{name: {...}}``."""
    skills_dir = Path(root) / "skills"
    graph: Dict[str, dict] = {}
    for directory in sorted(d for d in skills_dir.iterdir() if d.is_dir()):
        skill_md = directory / "SKILL.md"
        if not skill_md.is_file():
            continue
        front, _ = split_frontmatter(skill_md.read_text(encoding="utf-8"))
        if front is None:
            continue
        data = parse(front)
        metadata = data.get("metadata") or {}
        requires = [r.strip() for r in str(metadata.get("requires", "") or "").split(",") if r.strip()]
        graph[directory.name] = {
            "name": directory.name,
            "description": data.get("description", ""),
            "stage": metadata.get("stage", ""),
            "persona": metadata.get("persona", ""),
            "produces": metadata.get("produces", ""),
            "maturity": metadata.get("maturity", ""),
            "requires": requires,
        }
    for name, node in graph.items():
        node["unlocks"] = sorted(other for other, spec in graph.items() if name in spec["requires"])
    return graph


def tiers(graph: Dict[str, dict]) -> List[List[str]]:
    """Group plays into adoption waves: tier 0 has no prerequisites."""
    remaining: Set[str] = set(graph)
    placed: Set[str] = set()
    waves: List[List[str]] = []
    while remaining:
        wave = sorted(n for n in remaining if set(graph[n]["requires"]) <= placed)
        if not wave:  # a cycle; validate.py reports it, here we just stop cleanly
            waves.append(sorted(remaining))
            break
        waves.append(wave)
        placed |= set(wave)
        remaining -= set(wave)
    return waves


def render_text(graph: Dict[str, dict]) -> str:
    lines = ["AI-DLC adoption order", ""]
    for index, wave in enumerate(tiers(graph)):
        header = "Start here — no prerequisites" if index == 0 else f"Wave {index} — once wave {index - 1} is in place"
        lines.append(header)
        rows = []
        for name in wave:
            node = graph[name]
            rows.append(
                [
                    name,
                    str(node["stage"]),
                    str(node["maturity"]),
                    ", ".join(node["requires"]) or "—",
                    str(node["produces"]),
                ]
            )
        lines.append(render.table(["PLAY", "STAGE", "MATURITY", "REQUIRES", "PRODUCES"], rows))
        lines.append("")
    return "\n".join(lines).rstrip()


def render_mermaid(graph: Dict[str, dict]) -> str:
    lines = ["```mermaid", "graph LR"]
    for name, node in sorted(graph.items()):
        safe = name.replace("-", "_")
        lines.append(f'  {safe}["{name}"]')
        for dep in node["requires"]:
            lines.append(f"  {dep.replace('-', '_')} --> {safe}")
    lines.append("```")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-dlc adoption", description="Show the play dependency graph and rollout order")
    parser.add_argument("path", nargs="?", default=str(PACKAGE_ROOT), help="Package root")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--mermaid", action="store_true", help="Emit a Mermaid dependency graph")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    graph = load_graph(Path(args.path))
    if not graph:
        print("no skills found", file=sys.stderr)
        return 3
    if args.json:
        print(json.dumps({"schema": 1, "plays": graph, "waves": tiers(graph)}, indent=2))
    elif args.mermaid:
        print(render_mermaid(graph))
    else:
        print(render_text(graph))
    return 0


if __name__ == "__main__":
    sys.exit(main())
