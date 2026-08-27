#!/usr/bin/env python3
"""Thin wrapper so the repo works without installing the package."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai_dlc.install import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
