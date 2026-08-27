#!/usr/bin/env python3
"""Scaffold an AI-DLC project in a target repository."""

import argparse
import shutil
import sys
from pathlib import Path

AI_DLC_ROOT = Path(__file__).resolve().parent.parent


def scaffold(target: Path, client: str = "claude") -> None:
    if target is None:
        raise SystemExit("target path is required")

    target = Path(target).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)

    dirs = [
        target / "intent",
        target / "spec",
        target / "plan",
        target / "evals",
        target / ".claude" / "skills",
        target / ".claude" / "hooks",
        target / ".github",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    # Copy templates
    for name in ("intent.md", "spec.md", "plan.md", "REVIEW.md", "CLAUDE.md", "bands.yaml"):
        src = AI_DLC_ROOT / "templates" / name
        dst = target / name
        if not dst.exists():
            shutil.copy2(src, dst)

    # Copy governance hooks
    for hook in (AI_DLC_ROOT / "governance" / "hooks").glob("*.sh"):
        dst = target / ".claude" / "hooks" / hook.name
        if hook.name != "hook-template.sh" and not dst.exists():
            shutil.copy2(hook, dst)
            dst.chmod(0o755)

    # Copy settings.json
    src = AI_DLC_ROOT / "governance" / "settings.json"
    dst = target / ".claude" / "settings.json"
    if not dst.exists():
        shutil.copy2(src, dst)

    # Copy copilot instructions
    src = AI_DLC_ROOT / ".github" / "copilot-instructions.md"
    dst = target / ".github" / "copilot-instructions.md"
    if not dst.exists():
        shutil.copy2(src, dst)

    # Install skills for the requested client
    if client == "claude":
        skills_target = target / ".claude" / "skills"
        if skills_target.exists():
            shutil.rmtree(skills_target)
        shutil.copytree(AI_DLC_ROOT / "skills", skills_target)
    elif client == "codex":
        skills_target = target / ".codex" / "skills"
        if skills_target.exists():
            shutil.rmtree(skills_target)
        shutil.copytree(AI_DLC_ROOT / "skills", skills_target)
    else:
        skills_target = target / ".agents" / "skills"
        if skills_target.exists():
            shutil.rmtree(skills_target)
        shutil.copytree(AI_DLC_ROOT / "skills", skills_target)

    print(f"Scaffolded AI-DLC project at {target}")
    print(f"- Skills installed for {client}: {skills_target}")
    print("- Configure MCP by copying one of mcp/*.json to the client config location.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold an AI-DLC project")
    parser.add_argument("target", help="Path to the target repository")
    parser.add_argument("--client", default="claude", choices=["claude", "codex", "agents"])
    args = parser.parse_args()
    scaffold(args.target, args.client)
    return 0


if __name__ == "__main__":
    sys.exit(main())