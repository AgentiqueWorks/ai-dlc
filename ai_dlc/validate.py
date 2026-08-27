#!/usr/bin/env python3
"""Validate the AI-DLC package.

Every check returns a list of ``Problem`` records and ``run_all`` concatenates
them, so one broken skill no longer hides every MCP error the way the old
short-circuiting validator did.

The checks are the executable half of this repository's conventions: they keep
the skill graph acyclic, the frontmatter portable across agent clients, the MCP
fragments credential-free, and the documentation honest about which CLI
subcommands actually exist.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

from .catalog import load_indicator_catalog
from .repo import ARTIFACTS, STATUSES
from .yamlite import YamlLiteError, parse, split_frontmatter

__all__ = ["Problem", "run_all", "main", "CHECKS"]

ROOT = Path(__file__).resolve().parent.parent

ALLOWED_FRONTMATTER_KEYS = {"name", "description", "allowed-tools", "metadata", "license", "version"}
REQUIRED_FRONTMATTER_KEYS = {"name", "description"}

STAGES = {
    "00-onboarding",
    "01-plan",
    "02-design",
    "03-build",
    "04-test",
    "05-deploy",
    "06-maintain",
    "platform",
}
PERSONAS = {
    "originator",
    "pm",
    "product-owner",
    "designer",
    "engineer",
    "tech-lead",
    "qa",
    "code-owner",
    "release-manager",
    "sre",
    "security",
    "policy-owner",
    "platform",
    "service-owner",
}
MATURITY = {"stable", "beta", "experimental"}
REQUIRED_METADATA = ("stage", "persona", "requires", "produces", "indicators", "mcp", "maturity")

REQUIRED_HEADINGS = ("## Job", "## Steps", "## Output")

NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")
TOOL_RE = re.compile(r"^([A-Z][A-Za-z]*(\(.*\))?|mcp__[a-z0-9_-]+__[a-z0-9_*-]+)$")
REFERENCE_RE = re.compile(r"`(references/[A-Za-z0-9._/-]+)`")
TEMPLATE_RE = re.compile(r"`(templates/[A-Za-z0-9._/-]+)`")
CLI_MENTION_RE = re.compile(r"`?ai-dlc\s+([a-z][a-z-]*)")
CLI_FLAG_RE = re.compile(r"--[a-z][a-z0-9-]*")

# subcommand -> the callable that builds its parser, so documented flags can be
# checked the same way documented subcommands are.
SUBCOMMAND_PARSERS = {
    "validate": ("ai_dlc.validate", "build_parser"),
    "mcp-sync": ("ai_dlc.mcpsync", "build_parser"),
    "install": ("ai_dlc.install", "build_parser"),
    "init-repo": ("ai_dlc.scaffold", "build_init_parser"),
    "migrate": ("ai_dlc.scaffold", "build_migrate_parser"),
    "backlog": ("ai_dlc.backlog", "build_parser"),
    "metrics": ("ai_dlc.metrics", "build_parser"),
    "adoption": ("ai_dlc.adoption", "build_parser"),
}

REQUIRED_TEMPLATES = (
    "01-intent.md",
    "02-spec.md",
    "03-plan.md",
    "04-review.md",
    "05-deploy.md",
    "06-lessons.md",
    "REVIEW.md",
    "CLAUDE.md",
    "AGENTS.md",
    "bands.yaml",
    "metrics.md",
)

SECRET_PATTERNS = (
    ("openai-key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("anthropic-key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
    ("github-pat", re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b")),
    ("github-fine-grained", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("aws-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
)
PLACEHOLDER_RE = re.compile(r"^\$\{[A-Z][A-Z0-9_]*(:-[^}]*)?\}$")
CREDENTIALISH = re.compile(r"(token|key|secret|password|passwd|dsn|credential|api)", re.IGNORECASE)


@dataclass(frozen=True)
class Problem:
    level: str  # "error" | "warn"
    code: str
    path: str
    message: str

    def format(self) -> str:
        return f"{self.level.upper()}: [{self.code}] {self.path}: {self.message}"


def _rel(path: Path, root: Path) -> str:
    try:
        return str(Path(path).resolve().relative_to(Path(root).resolve()))
    except ValueError:
        return str(path)


def _skill_dirs(root: Path) -> List[Path]:
    skills = root / "skills"
    if not skills.is_dir():
        return []
    return sorted(d for d in skills.iterdir() if d.is_dir() and not d.name.startswith("."))


def _load_frontmatter(path: Path) -> tuple:
    raw = path.read_text(encoding="utf-8")
    front, body = split_frontmatter(raw)
    if front is None:
        return None, body, "missing YAML frontmatter"
    try:
        data = parse(front)
    except YamlLiteError as exc:
        return None, body, str(exc)
    if not isinstance(data, dict):
        return None, body, "frontmatter is not a mapping"
    return data, body, None


def _split_list(value: Any) -> List[str]:
    if value in (None, ""):
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [part.strip() for part in str(value).split(",") if part.strip()]


# --------------------------------------------------------------- skill checks


def check_skills(root: Path) -> List[Problem]:
    problems: List[Problem] = []
    dirs = _skill_dirs(root)
    if not dirs:
        return [Problem("error", "skill.missing", "skills/", "no skill directories found")]

    known_skills = {d.name for d in dirs}
    catalog = set(load_indicator_catalog())
    mcp_servers = {p.stem for p in (root / "mcp" / "configs").glob("*.json")}
    graph: Dict[str, List[str]] = {}

    for directory in dirs:
        skill_md = directory / "SKILL.md"
        rel = _rel(skill_md, root)
        if not skill_md.is_file():
            problems.append(Problem("error", "skill.missing", _rel(directory, root), "missing SKILL.md"))
            continue

        data, body, error = _load_frontmatter(skill_md)
        if error:
            problems.append(Problem("error", "skill.frontmatter.parse", rel, error))
            continue

        unknown = set(data) - ALLOWED_FRONTMATTER_KEYS
        for key in sorted(unknown):
            problems.append(
                Problem(
                    "error",
                    "skill.frontmatter.unknown-key",
                    rel,
                    f"top-level key '{key}' is not in the Agent Skills schema; nest custom data under 'metadata'",
                )
            )

        for field in sorted(REQUIRED_FRONTMATTER_KEYS - set(data)):
            problems.append(Problem("error", "skill.frontmatter.missing", rel, f"missing required field '{field}'"))
        if not REQUIRED_FRONTMATTER_KEYS.issubset(data):
            continue

        name = str(data["name"])
        description = str(data["description"])
        if name != directory.name:
            problems.append(
                Problem("error", "skill.name.mismatch", rel, f"name '{name}' does not match directory '{directory.name}'")
            )
        if not NAME_RE.match(name):
            problems.append(Problem("error", "skill.name.invalid", rel, f"name '{name}' is not a valid slug"))
        if "--" in name:
            problems.append(Problem("error", "skill.name.invalid", rel, f"name '{name}' has consecutive hyphens"))
        if len(name) > 64:
            problems.append(Problem("error", "skill.name.invalid", rel, f"name '{name}' is over 64 characters"))
        if len(description) > 1024:
            problems.append(Problem("error", "skill.description.length", rel, "description is over 1024 characters"))
        if len(description) < 40:
            problems.append(
                Problem("warn", "skill.description.thin", rel, "description is under 40 characters; models trigger on it")
            )
        if " Use " not in description and " use " not in description:
            problems.append(
                Problem("warn", "skill.description.no-trigger", rel, "description does not say when to use the skill")
            )

        problems.extend(_check_allowed_tools(data, body, rel))
        problems.extend(_check_metadata(data, rel, directory.name, known_skills, catalog, mcp_servers, graph))
        problems.extend(_check_body(directory, body, root, rel))

    problems.extend(_check_graph(graph))
    return problems


def _check_allowed_tools(data: dict, body: str, rel: str) -> List[Problem]:
    problems: List[Problem] = []
    tools = data.get("allowed-tools")
    if tools is None:
        return [Problem("warn", "skill.allowed-tools.missing", rel, "no allowed-tools; the skill runs with full tool access")]
    if not isinstance(tools, list):
        return [Problem("error", "skill.allowed-tools.shape", rel, "allowed-tools must be a block list")]
    for entry in tools:
        if not TOOL_RE.match(str(entry)):
            problems.append(Problem("error", "skill.allowed-tools.entry", rel, f"unrecognized tool spec {entry!r}"))
    names = {str(t).split("(")[0] for t in tools}
    writes = re.search(r"\b(write|draft|create|commit|update)\b", body, re.IGNORECASE)
    if writes and not names & {"Write", "Edit", "NotebookEdit"}:
        problems.append(
            Problem(
                "warn",
                "skill.allowed-tools.no-write",
                rel,
                "the steps describe authoring a file but neither Write nor Edit is allowed",
            )
        )
    return problems


def _check_metadata(
    data: dict,
    rel: str,
    skill_name: str,
    known_skills: Set[str],
    catalog: Set[str],
    mcp_servers: Set[str],
    graph: Dict[str, List[str]],
) -> List[Problem]:
    problems: List[Problem] = []
    metadata = data.get("metadata")
    if metadata is None:
        return [Problem("error", "skill.metadata.missing", rel, "missing 'metadata' block")]
    if not isinstance(metadata, dict):
        return [Problem("error", "skill.metadata.shape", rel, "metadata must be a mapping")]

    for key in REQUIRED_METADATA:
        if key not in metadata:
            problems.append(Problem("error", "skill.metadata.missing-key", rel, f"metadata is missing '{key}'"))

    for key, value in metadata.items():
        if isinstance(value, (list, dict)):
            problems.append(
                Problem(
                    "error",
                    "skill.metadata.shape",
                    rel,
                    f"metadata.{key} must be a string; the Skills API metadata contract is string-valued",
                )
            )

    stage = str(metadata.get("stage", ""))
    if stage and stage not in STAGES:
        problems.append(Problem("error", "skill.metadata.stage", rel, f"unknown stage '{stage}'"))

    for persona in _split_list(metadata.get("persona")):
        if persona not in PERSONAS:
            problems.append(Problem("error", "skill.metadata.persona", rel, f"unknown persona '{persona}'"))

    maturity = str(metadata.get("maturity", ""))
    if maturity and maturity not in MATURITY:
        problems.append(Problem("error", "skill.metadata.maturity", rel, f"unknown maturity '{maturity}'"))

    requires = _split_list(metadata.get("requires"))
    graph[skill_name] = requires
    for dep in requires:
        if dep == skill_name:
            problems.append(Problem("error", "skill.metadata.requires", rel, "a skill cannot require itself"))
        elif dep not in known_skills:
            problems.append(Problem("error", "skill.metadata.requires", rel, f"requires unknown skill '{dep}'"))

    for indicator in _split_list(metadata.get("indicators")):
        if catalog and indicator not in catalog:
            problems.append(
                Problem("error", "skill.metadata.indicator", rel, f"indicator '{indicator}' is not in references/indicators.yaml")
            )

    for server in _split_list(metadata.get("mcp")):
        if mcp_servers and server not in mcp_servers:
            problems.append(
                Problem("error", "skill.metadata.mcp", rel, f"MCP server '{server}' has no mcp/configs/{server}.json")
            )

    produces = str(metadata.get("produces", "")).strip()
    if produces:
        for item in _split_list(produces):
            ok = (
                item.startswith("intents/<id>/")
                or item in {"CLAUDE.md", "AGENTS.md", "REVIEW.md", "bands.yaml", "evals/", ".claude/settings.json"}
                or item.startswith(".claude/")
                or item.startswith("evals/")
                or item.startswith(".github/")
                or item.startswith("skills/")
                or item.startswith("lessons/")
                or item.startswith("metrics/")
            )
            if not ok:
                problems.append(
                    Problem("warn", "skill.metadata.produces", rel, f"unrecognized artifact path '{item}'")
                )
    return problems


def _check_graph(graph: Dict[str, List[str]]) -> List[Problem]:
    """Depth-first cycle detection over the play dependency graph."""
    problems: List[Problem] = []
    WHITE, GREY, BLACK = 0, 1, 2
    colour: Dict[str, int] = {node: WHITE for node in graph}

    def visit(node: str, trail: List[str]) -> None:
        colour[node] = GREY
        for dep in graph.get(node, []):
            if dep not in colour:
                continue
            if colour[dep] == GREY:
                cycle = " -> ".join(trail + [node, dep])
                problems.append(Problem("error", "skill.metadata.cycle", f"skills/{node}/SKILL.md", f"dependency cycle: {cycle}"))
            elif colour[dep] == WHITE:
                visit(dep, trail + [node])
        colour[node] = BLACK

    for node in sorted(graph):
        if colour.get(node) == WHITE:
            visit(node, [])
    return problems


def _check_body(directory: Path, body: str, root: Path, rel: str) -> List[Problem]:
    problems: List[Problem] = []
    for heading in REQUIRED_HEADINGS:
        if heading not in body:
            problems.append(Problem("error", "skill.body.heading", rel, f"missing required heading '{heading}'"))

    cited: Set[str] = set()
    for match in REFERENCE_RE.finditer(body):
        target = match.group(1)
        cited.add(target)
        candidate = directory / target
        if not candidate.is_file() and not (root / target).is_file():
            problems.append(Problem("error", "skill.body.reference", rel, f"cites '{target}' which does not exist"))

    refs_dir = directory / "references"
    if refs_dir.is_dir():
        for file in sorted(refs_dir.rglob("*")):
            if not file.is_file():
                continue
            relative = f"references/{file.relative_to(refs_dir).as_posix()}"
            if relative not in cited:
                problems.append(
                    Problem("warn", "skill.body.orphan-reference", _rel(file, root), "not cited from SKILL.md")
                )

    for match in TEMPLATE_RE.finditer(body):
        target = match.group(1)
        if not (root / target).exists():
            problems.append(Problem("error", "skill.body.template", rel, f"cites '{target}' which does not exist"))

    if len(body.splitlines()) > 400:
        problems.append(
            Problem("warn", "skill.body.length", rel, "SKILL.md is over 400 lines; move detail into references/")
        )
    return problems


# ----------------------------------------------------------------- mcp checks


def check_mcp(root: Path) -> List[Problem]:
    problems: List[Problem] = []
    configs = root / "mcp" / "configs"
    if not configs.is_dir():
        return [Problem("warn", "mcp.missing", "mcp/configs/", "directory not found")]

    valid_types = {"stdio", "http", "sse"}
    for path in sorted(configs.glob("*.json")):
        rel = _rel(path, root)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            problems.append(Problem("error", "mcp.json", rel, f"invalid JSON: {exc}"))
            continue

        if set(data) != {"mcpServers"}:
            problems.append(Problem("error", "mcp.fragment.shape", rel, "expected exactly one top-level key 'mcpServers'"))
            continue
        servers = data["mcpServers"]
        if not isinstance(servers, dict) or len(servers) != 1:
            problems.append(Problem("error", "mcp.fragment.shape", rel, "expected exactly one server per fragment"))
            continue
        name, server = next(iter(servers.items()))
        if name != path.stem:
            problems.append(Problem("error", "mcp.fragment.name", rel, f"server '{name}' does not match filename"))

        server_type = server.get("type")
        if server_type not in valid_types:
            problems.append(
                Problem("error", "mcp.fragment.type", rel, f"type '{server_type}' is not one of {sorted(valid_types)}")
            )
        if server_type == "stdio" and not server.get("command"):
            problems.append(Problem("error", "mcp.fragment.stdio", rel, "stdio server needs a 'command'"))
        if server_type in ("http", "sse") and not server.get("url"):
            problems.append(Problem("error", "mcp.fragment.remote", rel, f"{server_type} server needs a 'url'"))

        for section in ("env", "headers"):
            for key, value in (server.get(section) or {}).items():
                if not isinstance(value, str):
                    continue
                if not CREDENTIALISH.search(key) and not CREDENTIALISH.search(value):
                    continue
                candidate = value.replace("Bearer ", "").strip()
                if not PLACEHOLDER_RE.match(candidate):
                    problems.append(
                        Problem(
                            "error",
                            "mcp.placeholder",
                            rel,
                            f"{section}.{key} must be a ${{VAR}} placeholder, not a literal value",
                        )
                    )

    problems.extend(_check_mcp_drift(root))
    return problems


def _check_mcp_drift(root: Path) -> List[Problem]:
    from .mcpsync import build_configs

    try:
        expected = build_configs(root)
    except ValueError as exc:
        return [Problem("error", "mcp.sync", "mcp/configs/", str(exc))]

    problems: List[Problem] = []
    for filename, content in expected.items():
        path = root / "mcp" / filename
        if not path.is_file():
            problems.append(Problem("error", "mcp.sync.missing", f"mcp/{filename}", "run `ai-dlc mcp-sync`"))
            continue
        if path.read_text(encoding="utf-8") != content:
            problems.append(
                Problem("error", "mcp.sync.drift", f"mcp/{filename}", "out of date with mcp/configs/; run `ai-dlc mcp-sync`")
            )
    return problems


# --------------------------------------------------------------- other checks


def check_secrets(root: Path) -> List[Problem]:
    problems: List[Problem] = []
    for directory in ("mcp", "governance", "evals", "templates", "examples", "skills", "references"):
        base = root / directory
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix in (".png", ".jpg", ".gif", ".pdf"):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for label, pattern in SECRET_PATTERNS:
                if pattern.search(text):
                    problems.append(
                        Problem("error", "secret.literal", _rel(path, root), f"looks like a real {label}; use a ${{VAR}} placeholder")
                    )
    return problems


def check_hooks(root: Path) -> List[Problem]:
    from . import gitio

    problems: List[Problem] = []
    hooks_dir = root / "governance" / "hooks"
    if not hooks_dir.is_dir():
        return [Problem("warn", "hooks.missing", "governance/hooks/", "directory not found")]

    indexed: Dict[str, str] = {}
    if gitio.git_available() and gitio.repo_root(root):
        for line in gitio.git(["ls-files", "-s", "governance/hooks"], root, check=False).splitlines():
            parts = line.split()
            if len(parts) >= 4:
                indexed[parts[3]] = parts[0]

    for path in sorted(hooks_dir.glob("*.sh")):
        rel = _rel(path, root)
        text = path.read_text(encoding="utf-8")
        if not text.startswith("#!"):
            problems.append(Problem("error", "hooks.shebang", rel, "missing a shebang line"))
        elif "bash" not in text.splitlines()[0]:
            problems.append(Problem("warn", "hooks.shebang", rel, "shebang does not name bash"))
        if "set -euo pipefail" not in text:
            problems.append(Problem("error", "hooks.strict", rel, "missing 'set -euo pipefail'"))
        if not path.stat().st_mode & 0o111:
            problems.append(Problem("error", "hooks.exec", rel, "is not executable on disk"))
        mode = indexed.get(rel)
        if mode and mode != "100755":
            problems.append(
                Problem("error", "hooks.exec-index", rel, f"git index mode is {mode}; run `git update-index --chmod=+x {rel}`")
            )

    settings = root / "governance" / "settings.json"
    if settings.is_file():
        try:
            data = json.loads(settings.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return problems + [Problem("error", "hooks.settings", "governance/settings.json", f"invalid JSON: {exc}")]
        for group in (data.get("hooks") or {}).values():
            for entry in group:
                for hook in entry.get("hooks", []):
                    command = str(hook.get("command", ""))
                    match = re.search(r"\.claude/hooks/([A-Za-z0-9._-]+)", command)
                    if match and not (hooks_dir / match.group(1)).is_file():
                        problems.append(
                            Problem(
                                "error",
                                "hooks.settings-reference",
                                "governance/settings.json",
                                f"references {match.group(1)} which is not in governance/hooks/",
                            )
                        )
    return problems


def check_templates(root: Path) -> List[Problem]:
    problems: List[Problem] = []
    templates = root / "templates"
    if not templates.is_dir():
        return [Problem("error", "templates.missing", "templates/", "directory not found")]
    for name in REQUIRED_TEMPLATES:
        if not (templates / name).is_file():
            problems.append(Problem("error", "templates.missing", f"templates/{name}", "required template is missing"))
    return problems


def check_evals(root: Path) -> List[Problem]:
    problems: List[Problem] = []
    evals = root / "evals"
    if not evals.is_dir():
        return [Problem("warn", "evals.missing", "evals/", "directory not found")]
    for path in sorted(evals.glob("*.json")):
        rel = _rel(path, root)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            problems.append(Problem("error", "evals.json", rel, f"invalid JSON: {exc}"))
            continue
        for field in ("name", "prompt", "check"):
            if field not in data:
                problems.append(Problem("error", "evals.field", rel, f"missing '{field}'"))
        check = data.get("check")
        if check:
            script = root / check
            if not script.is_file():
                problems.append(Problem("error", "evals.check", rel, f"check script '{check}' does not exist"))
            elif not script.stat().st_mode & 0o111:
                problems.append(Problem("error", "evals.check-exec", check, "check script is not executable"))
    return problems


def check_examples(root: Path) -> List[Problem]:
    problems: List[Problem] = []
    base = root / "examples" / "intents"
    if not base.is_dir():
        return problems
    allowed = set(ARTIFACTS)
    for folder in sorted(p for p in base.iterdir() if p.is_dir()):
        rel = _rel(folder, root)
        present = []
        for path in sorted(folder.iterdir()):
            if not path.is_file():
                continue
            if path.name not in allowed:
                problems.append(Problem("error", "examples.artifact", _rel(path, root), "not a recognized chain artifact"))
                continue
            present.append(path.name)
        if "01-intent.md" not in present:
            problems.append(Problem("error", "examples.chain", rel, "missing 01-intent.md"))
        indexes = sorted(ARTIFACTS.index(n) for n in present)
        if indexes and indexes != list(range(indexes[0], indexes[0] + len(indexes))):
            problems.append(Problem("error", "examples.chain", rel, "artifact chain has a numeric gap"))
        for name in present:
            text = (folder / name).read_text(encoding="utf-8")
            match = re.search(r"^\s*[-*]\s*\*\*Status:?\*\*\s*(.+?)\s*$", text, re.MULTILINE | re.IGNORECASE)
            if match:
                value = match.group(1).strip().lower()
                if value not in STATUSES and not value.startswith("<"):
                    problems.append(
                        Problem("error", "examples.status", _rel(folder / name, root), f"unknown status '{value}'")
                    )
            if name == "03-plan.md" and "## Files that change" not in text:
                problems.append(
                    Problem(
                        "error",
                        "examples.plan-contract",
                        _rel(folder / name, root),
                        "missing '## Files that change'; plan-diff-alignment parses that section",
                    )
                )
    return problems


def check_docs(root: Path) -> List[Problem]:
    """Both directions: every subcommand is documented, every documented one exists."""
    from .cli import build_parser

    problems: List[Problem] = []
    parser = build_parser()
    subcommands: Set[str] = set()
    for action in parser._subparsers._group_actions if parser._subparsers else []:
        subcommands.update(getattr(action, "choices", {}) or {})

    docs = [
        root / "README.md",
        root / "CLAUDE.md",
        root / "AGENTS.md",
        root / "CONTRIBUTING.md",
        *sorted((root / "examples").glob("*.md")),
        *sorted((root / "references").glob("*.md")),
    ]
    mentioned: Set[str] = set()
    for doc in docs:
        if not doc.is_file():
            continue
        text = doc.read_text(encoding="utf-8")
        for match in CLI_MENTION_RE.finditer(text):
            word = match.group(1)
            if word in ("install", "validate"):
                mentioned.add(word)
                continue
            mentioned.add(word)
            if word not in subcommands:
                problems.append(
                    Problem("error", "docs.cli-unknown", _rel(doc, root), f"documents `ai-dlc {word}` which is not a subcommand")
                )

    problems.extend(_check_documented_flags(root, docs, subcommands))

    readme = root / "README.md"
    if readme.is_file():
        text = readme.read_text(encoding="utf-8")
        for command in sorted(subcommands):
            if f"ai-dlc {command}" not in text:
                problems.append(
                    Problem("warn", "docs.cli-undocumented", "README.md", f"subcommand `ai-dlc {command}` is not in the README")
                )
    return problems


def _subcommand_flags(command: str) -> Optional[Set[str]]:
    """Every option string a subcommand accepts, or None if unknown."""
    import importlib

    entry = SUBCOMMAND_PARSERS.get(command)
    if not entry:
        return None
    module_name, factory = entry
    try:
        parser = getattr(importlib.import_module(module_name), factory)()
    except (ImportError, AttributeError):
        return None
    flags: Set[str] = set()
    for action in parser._actions:
        flags.update(action.option_strings)
    return flags


def _check_documented_flags(root: Path, docs: List[Path], subcommands: Set[str]) -> List[Problem]:
    """A documented flag that does not exist is the same defect as a documented
    subcommand that does not exist -- it just fails later, in a user's terminal."""
    problems: List[Problem] = []
    cache: Dict[str, Optional[Set[str]]] = {}
    for doc in docs:
        if not doc.is_file():
            continue
        for lineno, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), start=1):
            match = CLI_MENTION_RE.search(line)
            if not match:
                continue
            command = match.group(1)
            if command not in subcommands:
                continue  # already reported as an unknown subcommand
            if command not in cache:
                cache[command] = _subcommand_flags(command)
            known = cache[command]
            if known is None:
                continue
            for flag in CLI_FLAG_RE.findall(line[match.end():]):
                if flag not in known:
                    problems.append(
                        Problem(
                            "error",
                            "docs.cli-unknown-flag",
                            f"{_rel(doc, root)}:{lineno}",
                            f"documents `ai-dlc {command} {flag}` but that flag does not exist",
                        )
                    )
    return problems


def check_indicators(root: Path) -> List[Problem]:
    """The registry and the catalog must not drift apart."""
    from .metrics import REGISTRY

    problems: List[Problem] = []
    catalog = load_indicator_catalog(root / "references" / "indicators.yaml")
    if not catalog:
        return [Problem("error", "indicators.missing", "references/indicators.yaml", "catalog is empty or missing")]

    local = {name for name, spec in catalog.items() if spec.get("computable") in ("git", "git-free", "conditional")}
    for name in sorted(local - set(REGISTRY)):
        problems.append(
            Problem("error", "indicators.unimplemented", "references/indicators.yaml", f"'{name}' claims to be computable but has no implementation")
        )
    for name in sorted(set(REGISTRY) - set(catalog)):
        problems.append(
            Problem("error", "indicators.uncatalogued", "ai_dlc/metrics.py", f"'{name}' is implemented but not catalogued")
        )
    for name in sorted(set(REGISTRY) & set(catalog)):
        if catalog[name].get("computable") == "external":
            problems.append(
                Problem("error", "indicators.mislabelled", "references/indicators.yaml", f"'{name}' is implemented but marked external")
            )
    for name, spec in sorted(catalog.items()):
        stage = str(spec.get("stage", ""))
        if stage and stage not in STAGES:
            problems.append(Problem("error", "indicators.stage", "references/indicators.yaml", f"'{name}' has unknown stage '{stage}'"))
    return problems


CHECKS: List[Callable[[Path], List[Problem]]] = [
    check_skills,
    check_mcp,
    check_templates,
    check_hooks,
    check_evals,
    check_examples,
    check_indicators,
    check_secrets,
    check_docs,
]


def run_all(root: Path = ROOT) -> List[Problem]:
    root = Path(root).resolve()
    problems: List[Problem] = []
    for check in CHECKS:
        try:
            problems.extend(check(root))
        except Exception as exc:  # a broken check must not hide the other checks
            problems.append(Problem("error", "check.crashed", check.__name__, f"{type(exc).__name__}: {exc}"))
    return problems


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-dlc validate", description="Validate the AI-DLC package")
    parser.add_argument("path", nargs="?", default=str(ROOT), help="Package root to validate")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--quiet", action="store_true", help="Only print the summary line")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    problems = run_all(Path(args.path))
    errors = [p for p in problems if p.level == "error"]
    warnings = [p for p in problems if p.level == "warn"]

    if args.json:
        print(json.dumps({"schema": 1, "problems": [asdict(p) for p in problems]}, indent=2))
    elif not args.quiet:
        for problem in sorted(problems, key=lambda p: (p.level != "error", p.path, p.code)):
            print(problem.format(), file=sys.stderr if problem.level == "error" else sys.stdout)

    failed = bool(errors) or (args.strict and bool(warnings))
    summary = f"{len(errors)} error(s), {len(warnings)} warning(s)"
    if failed:
        print(f"Validation failed: {summary}", file=sys.stderr)
        return 1
    print(f"Validation passed: {summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
