#!/usr/bin/env python3
"""Validate the ai-native-sdlc-skills repo."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
MCP_DIR = ROOT / "mcp"


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")


def _error(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)


def _warn(msg: str) -> None:
    print(f"WARN: {msg}", file=sys.stderr)


def _validate_frontmatter(skill_path: Path, raw: str) -> bool:
    ok = True
    match = FRONTMATTER_RE.match(raw)
    if not match:
        _error(f"{skill_path}: missing YAML frontmatter")
        return False

    body = match.group(1)
    data = {}
    for line in body.splitlines():
        if ":" not in line or line.strip().startswith("#"):
            continue
        key, _, value = line.partition(":")
        data[key.strip()] = value.strip()

    for field in ("name", "description"):
        if field not in data:
            _error(f"{skill_path}: missing required frontmatter field '{field}'")
            ok = False

    if ok:
        name = data["name"]
        expected = skill_path.parent.name
        if name != expected:
            _error(f"{skill_path}: name '{name}' does not match directory '{expected}'")
            ok = False
        if not NAME_RE.match(name):
            _error(f"{skill_path}: name '{name}' is not valid")
            ok = False
        if "--" in name:
            _error(f"{skill_path}: name '{name}' contains consecutive hyphens")
            ok = False
        if len(name) > 64:
            _error(f"{skill_path}: name '{name}' is over 64 characters")
            ok = False
        if len(data["description"]) > 1024:
            _error(f"{skill_path}: description is over 1024 characters")
            ok = False

    return ok


def validate_skills() -> bool:
    ok = True
    if not SKILLS_DIR.is_dir():
        _error(f"skills directory not found at {SKILLS_DIR}")
        return False

    skill_dirs = [d for d in SKILLS_DIR.iterdir() if d.is_dir()]
    if not skill_dirs:
        _warn("No skill directories found")

    for d in skill_dirs:
        skill_md = d / "SKILL.md"
        if not skill_md.is_file():
            _error(f"{d}: missing SKILL.md")
            ok = False
            continue
        raw = skill_md.read_text(encoding="utf-8")
        if not _validate_frontmatter(skill_md, raw):
            ok = False

    return ok


def validate_mcp() -> bool:
    ok = True
    if not MCP_DIR.is_dir():
        _warn(f"mcp directory not found at {MCP_DIR}")
        return True

    for path in MCP_DIR.rglob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            _error(f"{path}: invalid JSON: {e}")
            ok = False

    return ok


def main() -> int:
    ok = validate_skills() and validate_mcp()
    if ok:
        print("Validation passed.")
        return 0
    print("Validation failed.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())