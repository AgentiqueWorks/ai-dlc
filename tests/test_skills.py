import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
MCP_DIR = ROOT / "mcp"
TEMPLATES_DIR = ROOT / "templates"

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")


def test_all_skills_have_skill_md():
    skill_dirs = [d for d in SKILLS_DIR.iterdir() if d.is_dir()]
    assert skill_dirs, "No skill directories found"
    for d in skill_dirs:
        assert (d / "SKILL.md").is_file(), f"{d.name} missing SKILL.md"


def test_skill_frontmatter():
    for d in SKILLS_DIR.iterdir():
        if not d.is_dir():
            continue
        skill_md = d / "SKILL.md"
        raw = skill_md.read_text(encoding="utf-8")
        match = FRONTMATTER_RE.match(raw)
        assert match, f"{skill_md}: missing frontmatter"
        body = match.group(1)
        data = {}
        for line in body.splitlines():
            if ":" in line and not line.strip().startswith("#"):
                key, _, value = line.partition(":")
                data[key.strip()] = value.strip()
        assert "name" in data, f"{skill_md}: missing name"
        assert "description" in data, f"{skill_md}: missing description"
        assert data["name"] == d.name
        assert NAME_RE.match(data["name"]), f"{data['name']} is not a valid skill name"
        assert "--" not in data["name"]
        assert len(data["name"]) <= 64
        assert len(data["description"]) <= 1024


def test_mcp_json_is_valid():
    json_files = list(MCP_DIR.rglob("*.json"))
    assert json_files, "No MCP JSON files found"
    for path in json_files:
        json.loads(path.read_text(encoding="utf-8"))


def test_templates_exist():
    for name in ("intent.md", "spec.md", "plan.md", "REVIEW.md", "CLAUDE.md", "bands.yaml"):
        assert (TEMPLATES_DIR / name).is_file(), f"Missing template {name}"