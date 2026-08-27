#!/usr/bin/env python3
"""Regenerate combined MCP JSON files from mcp/configs/*.json."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIGS_DIR = ROOT / "mcp" / "configs"


def sync() -> None:
    base = {}
    for p in sorted(CONFIGS_DIR.glob("*.json")):
        data = json.loads(p.read_text())
        for k, v in data.get("mcpServers", {}).items():
            if k in base:
                raise ValueError(f"Duplicate MCP server name: {k}")
            base[k] = v

    (ROOT / "mcp" / "mcp.json").write_text(json.dumps(base, indent=2) + "\n")
    (ROOT / "mcp" / "claude-mcp.json").write_text(json.dumps({"servers": base}, indent=2) + "\n")
    (ROOT / "mcp" / "copilot-mcp.json").write_text(json.dumps({"mcpServers": base}, indent=2) + "\n")
    print(f"Regenerated mcp.json, claude-mcp.json, copilot-mcp.json with {len(base)} servers")


def main() -> int:
    sync()
    return 0


if __name__ == "__main__":
    sys.exit(main())