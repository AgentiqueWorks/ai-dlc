#!/usr/bin/env python3
"""Loaders for the package's machine-readable reference data."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from .yamlite import parse

__all__ = ["PACKAGE_ROOT", "load_indicator_catalog"]

PACKAGE_ROOT = Path(__file__).resolve().parent.parent


@lru_cache(maxsize=None)
def load_indicator_catalog(path: Path = None) -> Dict[str, Dict[str, Any]]:
    """Read ``references/indicators.yaml``.

    Returns an empty mapping when the file is absent so that a vendored copy of
    ``ai_dlc/`` without the reference tree still runs.
    """
    target = Path(path) if path else PACKAGE_ROOT / "references" / "indicators.yaml"
    if not target.is_file():
        return {}
    data = parse(target.read_text(encoding="utf-8"))
    indicators = data.get("indicators") if isinstance(data, dict) else None
    return indicators if isinstance(indicators, dict) else {}
