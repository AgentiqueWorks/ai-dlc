#!/usr/bin/env python3
"""Shared output helpers: fixed-width tables, durations, ratios."""

from __future__ import annotations

from typing import Iterable, List, Optional, Sequence

__all__ = ["table", "markdown_table", "fmt_duration", "fmt_ratio", "fmt_value", "bar"]


def fmt_duration(seconds: Optional[float]) -> str:
    if seconds is None:
        return "n/a"
    seconds = float(seconds)
    if seconds < 0:
        return "n/a"
    if seconds < 90:
        return f"{seconds:.0f}s"
    minutes = seconds / 60
    if minutes < 90:
        return f"{minutes:.0f}m"
    hours = minutes / 60
    if hours < 48:
        return f"{hours:.1f}h"
    return f"{hours / 24:.1f}d"


def fmt_ratio(value: Optional[float], as_percent: bool = True) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.0f}%" if as_percent else f"{value:.2f}"


def fmt_value(value, unit: str) -> str:
    if value is None:
        return "n/a"
    if unit == "duration":
        return fmt_duration(value)
    if unit == "ratio":
        return fmt_ratio(value)
    if unit == "count":
        return f"{value:g}" if isinstance(value, float) else str(value)
    return str(value)


def bar(filled: int, total: int) -> str:
    return "●" * filled + "○" * max(0, total - filled)


def table(headers: Sequence[str], rows: Iterable[Sequence[str]], gap: int = 2) -> str:
    """Render a left-aligned fixed-width table."""
    body: List[List[str]] = [[("" if c is None else str(c)) for c in row] for row in rows]
    if not body:
        return "  (nothing to show)"
    widths = [len(h) for h in headers]
    for row in body:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(cell))
    sep = " " * gap
    lines = [sep.join(h.ljust(widths[i]) for i, h in enumerate(headers)).rstrip()]
    for row in body:
        lines.append(sep.join(cell.ljust(widths[i]) for i, cell in enumerate(row)).rstrip())
    return "\n".join(lines)


def markdown_table(headers: Sequence[str], rows: Iterable[Sequence[str]]) -> str:
    body = [[("" if c is None else str(c)) for c in row] for row in rows]
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for row in body:
        out.append("| " + " | ".join(row) + " |")
    return "\n".join(out)
